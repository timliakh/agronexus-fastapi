<script setup>
import { ref, watch, onMounted } from "vue";
import { useRoute } from "vue-router";
import SiteHeader from "@/components/SiteHeader.vue";
import SiteFooter from "@/components/SiteFooter.vue";
import { useI18n } from "@/composables/useI18n";
import { pageUrl } from "@/utils/site";

const route = useRoute();
const { ui, loadUi, withLang, format, formatPrice } = useI18n();

const order = ref(null);
const products = ref([]);
const loading = ref(true);
const error = ref("");

async function loadOrder() {
  loading.value = true;
  error.value = "";
  order.value = null;
  products.value = [];

  try {
    await loadUi();
    const response = await fetch(withLang(`/orders/${route.params.id}`));
    if (!response.ok) throw new Error("not_found");
    order.value = await response.json();
    products.value = await Promise.all(
      order.value.items.map((item) =>
        fetch(withLang(`/products/${item.product_id}`)).then((r) => r.json()),
      ),
    );
    document.title = `${format("order_number", { id: order.value.id })} — ${ui.value.store_name}`;
  } catch {
    error.value = ui.value?.order_not_found || "Order not found.";
  } finally {
    loading.value = false;
  }
}

watch(() => route.params.id, loadOrder, { immediate: true });
onMounted(loadOrder);
</script>

<template>
  <SiteHeader active="catalog" />
  <main id="order">
    <p v-if="loading && ui">{{ ui.loading_order }}</p>
    <p v-else-if="error" class="error">
      {{ error }}
      <router-link :to="pageUrl('/')">{{ ui?.back_to_home?.replace("← ", "") || "Back" }}</router-link>
    </p>
    <article v-else-if="order && ui" class="card">
      <div class="success-icon">✓</div>
      <h1>{{ ui.order_success_title }}</h1>
      <p class="subtitle">{{ format("order_success_thanks", { name: order.customer_name }) }}</p>
      <div class="meta-row">
        <span>{{ format("order_number", { id: order.id }) }}</span>
        <span>{{ order.email }}</span>
      </div>
      <div class="items">
        <span class="label">{{ ui.order_items }}</span>
        <div v-for="(item, index) in order.items" :key="index" class="item">
          <div class="item-name">{{ products[index]?.name }}</div>
          <div class="item-meta">
            {{ item.configuration }} · {{ item.quantity }} × {{ formatPrice(products[index]?.price || 0) }}
          </div>
        </div>
      </div>
      <div class="total">
        <span>{{ ui.order_total }}</span>
        <span>{{ formatPrice(order.total_price) }}</span>
      </div>
    </article>
  </main>
  <SiteFooter />
</template>
