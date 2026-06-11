<script setup>
import { onMounted } from "vue";
import SiteHeader from "@/components/SiteHeader.vue";
import SiteFooter from "@/components/SiteFooter.vue";
import { useI18n } from "@/composables/useI18n";

const { ui, loadUi } = useI18n();

onMounted(loadUi);
</script>

<template>
  <SiteHeader active="about" />
  <main class="content-page">
    <article v-if="ui" class="content-card">
      <h1>{{ ui.about_title }}</h1>
      <p class="lead">{{ ui.about_intro }}</p>
      <section>
        <h2>{{ ui.about_mission_title }}</h2>
        <p>{{ ui.about_mission_text }}</p>
      </section>
      <section>
        <h2>{{ ui.about_tech_title }}</h2>
        <p>{{ ui.about_tech_text }}</p>
      </section>
    </article>
    <article v-else class="content-card">
      <p>...</p>
    </article>
  </main>
  <SiteFooter />
</template>
