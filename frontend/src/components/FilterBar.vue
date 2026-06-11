<script setup>
import { ref, computed, watch, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useI18n } from "@/composables/useI18n";
import { pageUrl, loadBrands } from "@/utils/site";

const route = useRoute();
const { ui, format } = useI18n();
const brandNames = ref({});

const filters = computed(() => ({
  category: route.query.category?.toString() || "",
  brand: route.query.brand?.toString() || "",
  q: route.query.q?.toString() || "",
}));

const visible = computed(
  () => filters.value.category || filters.value.brand || filters.value.q,
);

async function refreshBrands() {
  const brands = await loadBrands();
  brandNames.value = Object.fromEntries(brands.map((b) => [b.slug, b.name]));
}

watch(() => route.query.brand, refreshBrands, { immediate: true });
onMounted(refreshBrands);
</script>

<template>
  <div v-if="ui && visible" class="filter-bar-wrap">
    <div class="filter-bar">
      <span class="filter-label">{{ ui.filter_active }}:</span>
      <span v-if="filters.q" class="filter-chip">{{ filters.q }}</span>
      <span v-if="filters.category" class="filter-chip">
        {{ ui.categories[filters.category] || filters.category }}
      </span>
      <span v-if="filters.brand" class="filter-chip">
        {{ brandNames[filters.brand] || filters.brand }}
      </span>
      <router-link :to="pageUrl('/')" class="filter-clear">{{ ui.filter_clear }}</router-link>
    </div>
  </div>
</template>

<style scoped>
.filter-bar-wrap {
  margin-bottom: 1rem;
}
</style>
