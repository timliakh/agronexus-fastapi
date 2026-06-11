<script setup>
import { onMounted } from "vue";
import SiteHeader from "@/components/SiteHeader.vue";
import SiteFooter from "@/components/SiteFooter.vue";
import { useI18n } from "@/composables/useI18n";

const { ui, loadUi } = useI18n();

onMounted(loadUi);
</script>

<template>
  <SiteHeader active="contact" />
  <main class="content-page">
    <article v-if="ui" class="content-card">
      <h1>{{ ui.contact_title }}</h1>
      <p class="lead">{{ ui.contact_intro }}</p>
      <div class="contact-grid">
        <div class="contact-item">
          <span class="contact-label">{{ ui.contact_email_label }}</span>
          <a :href="`mailto:${ui.contact_email_value}`">{{ ui.contact_email_value }}</a>
        </div>
        <div class="contact-item">
          <span class="contact-label">{{ ui.contact_phone_label }}</span>
          <a :href="`tel:${ui.contact_phone_value.replace(/[^\d+]/g, '')}`">
            {{ ui.contact_phone_value }}
          </a>
        </div>
        <div class="contact-item">
          <span class="contact-label">{{ ui.contact_address_label }}</span>
          <span>{{ ui.contact_address_value }}</span>
        </div>
        <div class="contact-item">
          <span class="contact-label">{{ ui.contact_hours_label }}</span>
          <span>{{ ui.contact_hours_value }}</span>
        </div>
      </div>
    </article>
    <article v-else class="content-card">
      <p>...</p>
    </article>
  </main>
  <SiteFooter />
</template>
