<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useI18n } from "@/composables/useI18n";
import { productImageUrl } from "@/utils/site";

const route = useRoute();

const TOKEN_KEY = "admin_token";
const CATEGORY_KEYS = ["tractors", "harvesters", "plows", "seeders", "sprayers", "attachments"];

const { ui, loadUi, format, formatPrice } = useI18n();

const loggedIn = ref(false);
const loginError = ref(false);
const password = ref("");
const activeTab = ref("dashboard");

const stats = ref(null);
const products = ref([]);
const orders = ref([]);
const feedbacks = ref([]);

const form = ref(emptyForm());
const imagePreview = ref("");
const imageFile = ref(null);

const formTitle = computed(() => {
  if (!ui.value) return "";
  return form.value.id
    ? format("admin_edit_product", { id: form.value.id })
    : ui.value.admin_add_product;
});

function emptyForm() {
  return {
    id: "",
    name: "",
    description: "",
    price: "",
    category: "tractors",
    manufacturer: "",
    configurations: "",
    in_stock: "true",
    image_url: "",
  };
}

function token() {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(value) {
  localStorage.setItem(TOKEN_KEY, value);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }
  if (token()) headers["X-Admin-Token"] = token();

  const response = await fetch(path, { ...options, headers });
  if (response.status === 401) {
    clearToken();
    loggedIn.value = false;
    throw new Error("Unauthorized");
  }
  if (response.status === 204) return null;
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || "Request failed");
  }
  return response.json();
}

function showPreview(url) {
  imagePreview.value = url || "";
}

function onImageUrlInput() {
  showPreview(form.value.image_url.trim());
}

function onImageFileChange(event) {
  const file = event.target.files[0];
  imageFile.value = file || null;
  if (file) showPreview(URL.createObjectURL(file));
}

async function login() {
  try {
    const response = await fetch("/admin/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: password.value }),
    });
    const data = await response.json();
    if (!data.token) throw new Error("login failed");
    setToken(data.token);
    loginError.value = false;
    loggedIn.value = true;
    await loadAll();
  } catch {
    loginError.value = true;
  }
}

function logout() {
  clearToken();
  loggedIn.value = false;
}

function resetForm() {
  form.value = emptyForm();
  imageFile.value = null;
  showPreview("");
}

async function uploadProductImage(productId, file) {
  const formData = new FormData();
  formData.append("file", file);
  return api(`/admin/api/products/${productId}/image`, {
    method: "POST",
    body: formData,
  });
}

async function saveProduct(event) {
  event.preventDefault();
  const payload = {
    name: form.value.name,
    description: form.value.description,
    price: Number(form.value.price),
    category: form.value.category,
    manufacturer: form.value.manufacturer,
    configurations: form.value.configurations.split(",").map((s) => s.trim()).filter(Boolean),
    in_stock: form.value.in_stock === "true",
    image_url: form.value.image_url.trim() || null,
  };

  let productId = form.value.id;
  if (form.value.id) {
    await api(`/admin/api/products/${form.value.id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  } else {
    const created = await api("/admin/api/products", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    productId = created.id;
  }

  if (imageFile.value) {
    await uploadProductImage(productId, imageFile.value);
  }

  resetForm();
  await loadProducts();
  await loadStats();
}

function editProduct(product) {
  form.value = {
    id: String(product.id),
    name: product.name,
    description: product.description,
    price: String(product.price),
    category: product.category,
    manufacturer: product.manufacturer,
    configurations: product.configurations.join(", "),
    in_stock: product.in_stock ? "true" : "false",
    image_url: product.image_url || "",
  };
  imageFile.value = null;
  showPreview(productImageUrl(product));
  activeTab.value = "products";
}

async function deleteProduct(id) {
  if (!ui.value || !confirm(ui.value.admin_delete_product_confirm)) return;
  await api(`/admin/api/products/${id}`, { method: "DELETE" });
  await loadProducts();
  await loadStats();
}

async function deleteFeedback(id) {
  if (!ui.value || !confirm(ui.value.admin_delete_feedback_confirm)) return;
  await api(`/admin/api/feedbacks/${id}`, { method: "DELETE" });
  await loadFeedbacks();
  await loadStats();
}

async function loadStats() {
  stats.value = await api("/admin/api/stats");
}

async function loadProducts() {
  products.value = await api("/admin/api/products");
}

async function loadOrders() {
  orders.value = await api("/admin/api/orders");
}

async function loadFeedbacks() {
  feedbacks.value = await api("/admin/api/feedbacks");
}

async function loadAll() {
  await Promise.all([loadStats(), loadProducts(), loadOrders(), loadFeedbacks()]);
}

onMounted(async () => {
  await loadUi();
  if (token()) {
    loggedIn.value = true;
    loadAll().catch(() => {
      loggedIn.value = false;
    });
  }
});
</script>

<template>
  <header v-if="ui">
    <div>
      <h1 class="admin-title">{{ ui.admin_title }}</h1>
      <small>{{ ui.admin_subtitle }}</small>
    </div>
    <div class="header-actions">
      <router-link :to="{ path: '/', query: route.query }">{{ ui.admin_back_to_site }}</router-link>
      <button v-if="loggedIn" class="btn-secondary" @click="logout">{{ ui.admin_logout }}</button>
    </div>
  </header>

  <main v-if="ui">
    <section v-if="!loggedIn" class="card login-card">
      <h2>{{ ui.admin_login_title }}</h2>
      <label>{{ ui.admin_password_label }}</label>
      <input v-model="password" type="password" class="full-width-input" @keyup.enter="login" />
      <div class="actions">
        <button class="btn-primary" @click="login">{{ ui.admin_login_btn }}</button>
      </div>
      <p v-if="loginError" class="error">{{ ui.admin_login_error }}</p>
    </section>

    <section v-else>
      <div class="tabs">
        <button :class="{ active: activeTab === 'dashboard' }" @click="activeTab = 'dashboard'">{{ ui.admin_tab_dashboard }}</button>
        <button :class="{ active: activeTab === 'products' }" @click="activeTab = 'products'">{{ ui.admin_tab_products }}</button>
        <button :class="{ active: activeTab === 'orders' }" @click="activeTab = 'orders'">{{ ui.admin_tab_orders }}</button>
        <button :class="{ active: activeTab === 'feedbacks' }" @click="activeTab = 'feedbacks'">{{ ui.admin_tab_feedbacks }}</button>
      </div>

      <section v-show="activeTab === 'dashboard'" class="tab card">
        <h2>{{ ui.admin_overview }}</h2>
        <div v-if="stats" class="stats">
          <div class="stat"><span>{{ ui.admin_stat_products }}</span><strong>{{ stats.products_count }}</strong></div>
          <div class="stat"><span>{{ ui.admin_stat_orders }}</span><strong>{{ stats.orders_count }}</strong></div>
          <div class="stat"><span>{{ ui.admin_stat_feedbacks }}</span><strong>{{ stats.feedbacks_count }}</strong></div>
          <div class="stat"><span>{{ ui.admin_stat_revenue }}</span><strong>{{ formatPrice(stats.total_revenue) }}</strong></div>
        </div>
      </section>

      <section v-show="activeTab === 'products'" class="tab card">
        <h2>{{ ui.admin_products_title }}</h2>
        <table v-if="products.length">
          <thead>
            <tr>
              <th>{{ ui.admin_table_photo }}</th>
              <th>{{ ui.admin_table_id }}</th>
              <th>{{ ui.admin_table_name }}</th>
              <th>{{ ui.admin_table_price }}</th>
              <th>{{ ui.admin_table_category }}</th>
              <th>{{ ui.admin_table_stock }}</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="product in products" :key="product.id">
              <td><img class="product-thumb" :src="productImageUrl(product)" alt="" /></td>
              <td>{{ product.id }}</td>
              <td>{{ product.name }}</td>
              <td>{{ formatPrice(product.price) }}</td>
              <td>{{ ui.categories[product.category] || product.category }}</td>
              <td>{{ product.in_stock ? ui.admin_yes : ui.admin_no }}</td>
              <td>
                <button class="btn-secondary" @click="editProduct(product)">{{ ui.admin_edit_btn }}</button>
                <button class="btn-danger" @click="deleteProduct(product.id)">{{ ui.admin_delete_btn }}</button>
              </td>
            </tr>
          </tbody>
        </table>
        <hr />
        <h3>{{ formTitle }}</h3>
        <form @submit="saveProduct">
          <div class="form-grid">
            <div><label>{{ ui.admin_product_name }}</label><input v-model="form.name" required /></div>
            <div><label>{{ ui.admin_product_price }}</label><input v-model="form.price" type="number" step="0.01" min="0.01" required /></div>
            <div>
              <label>{{ ui.admin_product_category }}</label>
              <select v-model="form.category" required>
                <option v-for="key in CATEGORY_KEYS" :key="key" :value="key">
                  {{ ui.categories[key] }}
                </option>
              </select>
            </div>
            <div><label>{{ ui.admin_product_manufacturer }}</label><input v-model="form.manufacturer" required /></div>
            <div><label>{{ ui.admin_product_configurations }}</label><input v-model="form.configurations" required /></div>
            <div>
              <label>{{ ui.admin_product_in_stock }}</label>
              <select v-model="form.in_stock">
                <option value="true">{{ ui.admin_yes }}</option>
                <option value="false">{{ ui.admin_no }}</option>
              </select>
            </div>
            <div><label>{{ ui.admin_product_image_url }}</label><input v-model="form.image_url" @input="onImageUrlInput" /></div>
          </div>
          <div class="field-block">
            <label>{{ ui.admin_product_upload }}</label>
            <input type="file" accept="image/jpeg,image/png,image/webp,image/gif" class="full-width-input" @change="onImageFileChange" />
          </div>
          <div v-if="imagePreview" class="image-preview">
            <img :src="imagePreview" alt="Preview" />
          </div>
          <div class="field-block">
            <label>{{ ui.admin_product_description }}</label>
            <textarea v-model="form.description" required />
          </div>
          <div class="actions">
            <button type="submit" class="btn-primary">{{ ui.admin_save }}</button>
            <button type="button" class="btn-secondary" @click="resetForm">{{ ui.admin_reset }}</button>
          </div>
        </form>
      </section>

      <section v-show="activeTab === 'orders'" class="tab card">
        <h2>{{ ui.admin_orders_title }}</h2>
        <table v-if="orders.length">
          <thead>
            <tr>
              <th>{{ ui.admin_table_id }}</th>
              <th>{{ ui.admin_table_client }}</th>
              <th>{{ ui.admin_table_email }}</th>
              <th>{{ ui.admin_table_amount }}</th>
              <th>{{ ui.admin_table_items }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in orders" :key="order.id">
              <td>{{ order.id }}</td>
              <td>{{ order.customer_name }}</td>
              <td>{{ order.email }}</td>
              <td>{{ formatPrice(order.total_price) }}</td>
              <td>
                <div v-for="item in order.items" :key="`${order.id}-${item.product_id}-${item.configuration}`">
                  #{{ item.product_id }} × {{ item.quantity }} ({{ item.configuration }})
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else>{{ ui.admin_no_orders }}</p>
      </section>

      <section v-show="activeTab === 'feedbacks'" class="tab card">
        <h2>{{ ui.admin_feedbacks_title }}</h2>
        <table v-if="feedbacks.length">
          <thead>
            <tr>
              <th>{{ ui.admin_table_id }}</th>
              <th>{{ ui.admin_table_name }}</th>
              <th>{{ ui.admin_table_email }}</th>
              <th>{{ ui.admin_table_message }}</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="feedback in feedbacks" :key="feedback.id">
              <td>{{ feedback.id }}</td>
              <td>{{ feedback.name }} <span v-if="feedback.is_premium" class="badge">{{ ui.admin_vip_badge }}</span></td>
              <td>{{ feedback.email }}<br />{{ feedback.phone || "" }}</td>
              <td>{{ feedback.message }}</td>
              <td><button class="btn-danger" @click="deleteFeedback(feedback.id)">{{ ui.admin_delete_btn }}</button></td>
            </tr>
          </tbody>
        </table>
        <p v-else>{{ ui.admin_no_feedbacks }}</p>
      </section>
    </section>
  </main>
</template>
