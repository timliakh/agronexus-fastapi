<script setup>
import { watch } from "vue";
import { useRoute } from "vue-router";
import { useI18n } from "@/composables/useI18n";

const route = useRoute();
const { lang, ui, loadUi } = useI18n();

watch(
  () => route.query.lang,
  async (value) => {
    if (typeof value === "string" && value !== lang.value) {
      lang.value = value;
      await loadUi();
    }
  },
);

watch(
  () => route.meta.bodyClass,
  (bodyClass) => {
    document.body.className = bodyClass || "";
  },
  { immediate: true },
);

watch(
  [ui, () => route.meta.titleKey],
  () => {
    if (!ui.value) return;
    const key = route.meta.titleKey;
    document.documentElement.lang = lang.value;
    document.title = key ? `${ui.value[key]} — ${ui.value.store_name}` : ui.value.store_name;
  },
  { immediate: true },
);
</script>

<template>
  <router-view />
</template>
