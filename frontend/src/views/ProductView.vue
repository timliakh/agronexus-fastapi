<script setup>
import { ref, computed, watch, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import SiteHeader from "@/components/SiteHeader.vue";
import SiteFooter from "@/components/SiteFooter.vue";
import { useI18n } from "@/composables/useI18n";
import { productImageUrl, pageUrl } from "@/utils/site";

const route = useRoute();
const router = useRouter();
const { lang, ui, loadUi, withLang, formatPrice, apiError } = useI18n();

const product = ref(null);
const loading = ref(true);
const error = ref("");
const formError = ref("");
const submitting = ref(false);

const form = ref({
  customer_name: "",
  email: "",
  configuration: "",
  quantity: 1,
});

const orderTotal = computed(() => {
  if (!product.value) return "";
  const qty = Math.max(1, Math.min(10, Number(form.value.quantity) || 1));
  return formatPrice(product.value.price * qty);
});

async function loadProduct() {
  loading.value = true;
  error.value = "";
  product.value = null;

  try {
    await loadUi();
    const slug = route.params.slug;

    if (/^\d+$/.test(slug)) {
      const response = await fetch(withLang(`/products/${slug}`));
      if (!response.ok) throw new Error("not_found");
      const data = await response.json();
      router.replace({
        path: `/catalog/${data.slug}`,
        query: route.query,
      });
      return;
    }

    const response = await fetch(withLang(`/products/${encodeURIComponent(slug)}`));
    if (!response.ok) throw new Error("not_found");
    product.value = await response.json();
    form.value.configuration = product.value.configurations[0] || "";

    const canonical = document.querySelector('link[rel="canonical"]')
      || (() => {
        const link = document.createElement("link");
        link.rel = "canonical";
        document.head.appendChild(link);
        return link;
      })();
    canonical.href = `${window.location.origin}/catalog/${product.value.slug}`;
    document.title = `${product.value.name} — ${ui.value.store_name}`;
  } catch {
    error.value = ui.value?.product_not_found || "Product not found.";
  } finally {
    loading.value = false;
  }
}

async function submitOrder(event) {
  event.preventDefault();
  formError.value = "";
  submitting.value = true;

  try {
    const response = await fetch("/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        customer_name: form.value.customer_name.trim(),
        email: form.value.email.trim(),
        items: [{
          product_id: product.value.id,
          configuration: form.value.configuration,
          quantity: Number(form.value.quantity),
        }],
      }),
    });

    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(apiError(data.detail, ui.value.order_submit_error));
    }

    const order = await response.json();
    router.push({ path: `/order/${order.id}`, query: { lang: lang.value } });
  } catch (err) {
    formError.value = err.message || ui.value.order_submit_error;
    submitting.value = false;
  }
}

watch(() => route.params.slug, loadProduct, { immediate: true });
onMounted(loadProduct);
</script>

<template>
  <SiteHeader active="catalog" />
  <main id="product">
    <p v-if="loading && ui">{{ ui.loading_product }}</p>
    <p v-else-if="error" class="error">
      {{ error }}
      <router-link :to="pageUrl('/')">{{ ui?.back_to_catalog?.replace("← ", "") || "Back" }}</router-link>
    </p>
    <article v-else-if="product && ui" class="card">
      <div class="product-image">
        <img :src="productImageUrl(product)" :alt="product.name" />
      </div>
      <div class="card-content">
        <div class="card-top">
          <span class="category">{{ ui.categories[product.category] || product.category }}</span>
          <span class="autonomous-badge">{{ ui.autonomous || "AUTONOMOUS" }}</span>
        </div>
        <h1>{{ product.name }}</h1>
        <p class="description">{{ product.description }}</p>
        <p class="meta">
          <span class="label">{{ ui.manufacturer }}</span>
          <strong class="manufacturer-name">{{ product.manufacturer }}</strong>
        </p>
        <p class="price">{{ formatPrice(product.price) }}</p>
        <p class="meta">
          <span class="label">{{ ui.configurations }}</span>
        </p>
        <div class="configurations">
          <span v-for="config in product.configurations" :key="config" class="badge">{{ config }}</span>
        </div>
        <span class="stock" :class="product.in_stock ? 'available' : 'unavailable'">
          {{ product.in_stock ? ui.in_stock : ui.out_of_stock }}
        </span>

        <section v-if="product.in_stock" class="purchase">
          <h2>{{ ui.purchase_title }}</h2>
          <form @submit="submitOrder">
            <div class="form-grid">
              <div class="field">
                <label for="customer-name">{{ ui.customer_name }}</label>
                <input id="customer-name" v-model="form.customer_name" required minlength="2" maxlength="50" />
              </div>
              <div class="field">
                <label for="customer-email">{{ ui.customer_email }}</label>
                <input id="customer-email" v-model="form.email" type="email" required />
              </div>
              <div class="field">
                <label for="configuration">{{ ui.select_configuration }}</label>
                <select id="configuration" v-model="form.configuration" required>
                  <option v-for="config in product.configurations" :key="config" :value="config">
                    {{ config }}
                  </option>
                </select>
              </div>
              <div class="field">
                <label for="quantity">{{ ui.quantity }}</label>
                <input id="quantity" v-model.number="form.quantity" type="number" min="1" max="10" required />
              </div>
            </div>
            <div class="order-total">
              <span>{{ ui.order_total }}</span>
              <span>{{ orderTotal }}</span>
            </div>
            <button type="submit" class="btn-buy" :disabled="submitting">{{ ui.submit_order }}</button>
            <p v-if="formError" class="form-error">{{ formError }}</p>
          </form>
        </section>
      </div>
    </article>
  </main>
  <SiteFooter />
</template>
