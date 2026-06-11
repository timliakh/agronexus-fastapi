<script setup>
import { ref, watch, onMounted } from "vue";
import { useRoute } from "vue-router";
import SiteHeader from "@/components/SiteHeader.vue";
import SiteFooter from "@/components/SiteFooter.vue";
import FilterBar from "@/components/FilterBar.vue";
import { useI18n } from "@/composables/useI18n";
import { productImageUrl } from "@/utils/site";

const route = useRoute();
const { lang, ui, loadUi, format, formatPrice } = useI18n();

const products = ref([]);
const loading = ref(true);
const error = ref("");

function buildProductsUrl() {
  const params = new URLSearchParams();
  params.set("lang", lang.value);
  if (route.query.category) params.set("category", route.query.category.toString());
  if (route.query.brand) params.set("brand", route.query.brand.toString());
  if (route.query.q) params.set("q", route.query.q.toString());
  return `/products?${params.toString()}`;
}

async function loadCatalog() {
  loading.value = true;
  error.value = "";
  try {
    await loadUi();
    const response = await fetch(buildProductsUrl());
    if (!response.ok) throw new Error("load failed");
    products.value = await response.json();
  } catch {
    error.value = ui.value?.load_error || "Failed to load catalog.";
  } finally {
    loading.value = false;
  }
}

watch(() => [route.query.category, route.query.brand, route.query.q, lang.value], loadCatalog, {
  immediate: true,
});

onMounted(loadCatalog);
</script>

<template>
  <SiteHeader active="catalog" />
  <main>
    <FilterBar />
    <section id="catalog">
      <p v-if="loading && ui">{{ ui.loading_catalog }}</p>
      <p v-else-if="error" class="error">{{ error }}</p>
      <p v-else-if="ui && !products.length" class="empty-state">
        {{
          route.query.q
            ? format("search_no_results", { q: route.query.q })
            : ui.catalog_empty
        }}
      </p>
      <template v-else-if="ui">
        <router-link
          v-for="product in products"
          :key="product.id"
          :to="`/catalog/${product.slug}?lang=${lang}`"
          class="card-link"
        >
          <article class="card">
            <div class="card-image">
              <img :src="productImageUrl(product)" :alt="product.name" loading="lazy" />
            </div>
            <div class="card-header">
              <span class="category">{{ ui.categories[product.category] || product.category }}</span>
              <span class="autonomous-badge">{{ ui.autonomous || "AUTONOMOUS" }}</span>
            </div>
            <div class="card-body">
              <h2>{{ product.name }}</h2>
              <p class="card-desc">{{ product.description }}</p>
              <p class="manufacturer">{{ product.manufacturer }}</p>
              <div class="specs">
                <span v-for="config in product.configurations" :key="config" class="spec-chip">
                  {{ config }}
                </span>
              </div>
              <div class="card-footer">
                <span class="price">{{ formatPrice(product.price) }}</span>
                <span class="more">{{ ui.more }}</span>
              </div>
            </div>
          </article>
        </router-link>
      </template>
    </section>
  </main>
  <SiteFooter />
</template>
