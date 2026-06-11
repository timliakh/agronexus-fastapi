<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useI18n } from "@/composables/useI18n";
import { catalogUrl, pageUrl, loadBrands } from "@/utils/site";

const props = defineProps({
  active: { type: String, default: "catalog" },
});

const CATEGORY_KEYS = ["tractors", "harvesters", "plows", "seeders", "sprayers", "attachments"];

const route = useRoute();
const router = useRouter();
const { lang, ui, setLang, format, formatPrice, languages, languageLabels } = useI18n();

const brands = ref([]);
const searchQuery = ref("");
const suggestions = ref([]);
const showSuggestions = ref(false);
const openDropdown = ref(null);
let searchTimer = null;

const filters = computed(() => ({
  category: route.query.category?.toString() || "",
  brand: route.query.brand?.toString() || "",
  q: route.query.q?.toString() || "",
}));

onMounted(async () => {
  searchQuery.value = filters.value.q;
  brands.value = await loadBrands();
});

function navClass(page) {
  return props.active === page ? "nav-link active" : "nav-link";
}

function dropdownClass(isActive) {
  return isActive ? "dropdown-item active" : "dropdown-item";
}

function toggleDropdown(name) {
  openDropdown.value = openDropdown.value === name ? null : name;
}

function closeDropdowns() {
  openDropdown.value = null;
}

function onLangChange(event) {
  setLang(event.target.value);
}

function navigateSearch(query) {
  const trimmed = query.trim();
  router.push({
    path: "/",
    query: {
      lang: lang.value,
      ...(filters.value.category ? { category: filters.value.category } : {}),
      ...(filters.value.brand ? { brand: filters.value.brand } : {}),
      ...(trimmed ? { q: trimmed } : {}),
    },
  });
}

function onSearchInput() {
  clearTimeout(searchTimer);
  const value = searchQuery.value.trim();
  if (value.length < 2) {
    suggestions.value = [];
    showSuggestions.value = false;
    return;
  }

  searchTimer = setTimeout(async () => {
    const params = new URLSearchParams();
    params.set("lang", lang.value);
    params.set("q", value);
    if (filters.value.category) params.set("category", filters.value.category);
    if (filters.value.brand) params.set("brand", filters.value.brand);

    const response = await fetch(`/products/suggest?${params.toString()}`);
    if (!response.ok) {
      suggestions.value = [];
      showSuggestions.value = false;
      return;
    }

    suggestions.value = await response.json();
    showSuggestions.value = true;
  }, 220);
}

function onSearchKeydown(event) {
  if (event.key === "Enter") {
    event.preventDefault();
    showSuggestions.value = false;
    navigateSearch(searchQuery.value);
  }
  if (event.key === "Escape") {
    showSuggestions.value = false;
  }
}

function onDocumentClick(event) {
  if (!event.target.closest("[data-site-search]")) {
    showSuggestions.value = false;
  }
  if (!event.target.closest(".nav-dropdown")) {
    closeDropdowns();
  }
}

onMounted(() => document.addEventListener("click", onDocumentClick));
onUnmounted(() => document.removeEventListener("click", onDocumentClick));
</script>

<template>
  <header v-if="ui" class="site-header" role="banner">
    <div class="header-top">
      <div class="brand-block">
        <router-link :to="pageUrl('/')" class="logo-link">
          <span class="logo-title">{{ ui.store_name }}</span>
          <span class="tagline">{{ ui.tagline }}</span>
        </router-link>
      </div>

      <div class="site-search" data-site-search>
        <input
          v-model="searchQuery"
          type="search"
          class="site-search-input"
          :placeholder="ui.search_placeholder"
          autocomplete="off"
          :aria-label="ui.search_placeholder"
          @input="onSearchInput"
          @keydown="onSearchKeydown"
        />
        <div
          v-if="showSuggestions"
          class="search-suggestions"
          role="listbox"
        >
          <div v-if="!suggestions.length" class="search-empty">
            {{ format("search_no_results", { q: searchQuery.trim() }) }}
          </div>
          <router-link
            v-for="product in suggestions"
            :key="product.id"
            :to="`/catalog/${product.slug}?lang=${lang}`"
            class="search-suggestion"
            role="option"
            @click="showSuggestions = false"
          >
            <span class="search-suggestion-name">{{ product.name }}</span>
            <span class="search-suggestion-meta">
              {{ product.manufacturer }} · {{ formatPrice(product.price) }}
            </span>
          </router-link>
        </div>
      </div>

      <nav class="site-nav" aria-label="Main">
        <router-link :to="pageUrl('/')" :class="navClass('catalog')">{{ ui.nav_catalog }}</router-link>

        <div class="nav-dropdown" :class="{ open: openDropdown === 'categories' }">
          <button type="button" class="nav-dropdown-toggle" @click.stop="toggleDropdown('categories')">
            {{ ui.nav_categories }} ▾
          </button>
          <div class="dropdown-menu">
            <router-link
              :to="catalogUrl({ brand: filters.brand || undefined, q: filters.q || undefined })"
              :class="dropdownClass(!filters.category)"
            >
              {{ ui.nav_all_categories }}
            </router-link>
            <router-link
              v-for="key in CATEGORY_KEYS"
              :key="key"
              :to="catalogUrl({ category: key, brand: filters.brand || undefined, q: filters.q || undefined })"
              :class="dropdownClass(filters.category === key)"
            >
              {{ ui.categories[key] || key }}
            </router-link>
          </div>
        </div>

        <div class="nav-dropdown" :class="{ open: openDropdown === 'brands' }">
          <button type="button" class="nav-dropdown-toggle" @click.stop="toggleDropdown('brands')">
            {{ ui.nav_brands }} ▾
          </button>
          <div class="dropdown-menu">
            <router-link
              :to="catalogUrl({ category: filters.category || undefined, q: filters.q || undefined })"
              :class="dropdownClass(!filters.brand)"
            >
              {{ ui.nav_all_brands }}
            </router-link>
            <router-link
              v-for="brand in brands"
              :key="brand.slug"
              :to="catalogUrl({ category: filters.category || undefined, brand: brand.slug, q: filters.q || undefined })"
              :class="dropdownClass(filters.brand === brand.slug)"
            >
              {{ brand.name }}
            </router-link>
          </div>
        </div>

        <router-link :to="pageUrl('/about')" :class="navClass('about')">{{ ui.nav_about }}</router-link>
        <router-link :to="pageUrl('/contact')" :class="navClass('contact')">{{ ui.nav_contact }}</router-link>
      </nav>

      <label class="lang-switch">
        {{ ui.language }}:
        <select :value="lang" @change="onLangChange">
          <option v-for="code in languages" :key="code" :value="code">
            {{ languageLabels[code] || code }}
          </option>
        </select>
      </label>
    </div>
  </header>
</template>
