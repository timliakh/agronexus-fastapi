<script setup>
import { computed } from "vue";
import { useI18n } from "@/composables/useI18n";

const SOCIAL_LINKS = [
  {
    id: "telegram",
    url: "https://t.me/",
    labelKey: "social_telegram",
    icon: `<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M9.9 16.2 9.7 20c.4 0 .6-.2.8-.4l1.9-1.8 4 2.9c.7.4 1.2.2 1.4-.7l2.6-12.2c.3-1.1-.4-1.5-1.2-1.2L3.6 9.8c-1.1.4-1.1 1 0 1.3l4.6 1.4 10.7-6.7c.5-.3 1-.1.6.2"/></svg>`,
  },
  {
    id: "x",
    url: "https://x.com/",
    labelKey: "social_x",
    icon: `<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M17.3 3h3.4l-7.4 8.5L22 21h-6.8l-5.3-6.9L4 21H.6l8-9.2L2 3h7l4.8 6.3L17.3 3zm-1.2 16.2h1.9L7.1 4.8H5.1l11 14.4z"/></svg>`,
  },
  {
    id: "linkedin",
    url: "https://www.linkedin.com/",
    labelKey: "social_linkedin",
    icon: `<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M6.5 8.7H2.4v12.7h4.1V8.7zM4.5 2.3a2.4 2.4 0 1 0 0 4.8 2.4 2.4 0 0 0 0-4.8zm6.1 6.4H6.7v12.7h3.9v-6.3c0-1.6.3-3.2 2.3-3.2 2 0 2 1.9 2 3.3v6.2h3.9v-6.6c0-3.6-.8-6.3-4.9-6.3-2 0-3.3 1.1-3.8 2.1v-.2h-.1z"/></svg>`,
  },
  {
    id: "youtube",
    url: "https://www.youtube.com/",
    labelKey: "social_youtube",
    icon: `<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M21.6 7.2a2.5 2.5 0 0 0-1.8-1.8C18 5 12 5 12 5s-6 0-7.8.4a2.5 2.5 0 0 0-1.8 1.8C2 9 2 12 2 12s0 3 .4 4.8a2.5 2.5 0 0 0 1.8 1.8C6 19 12 19 12 19s6 0 7.8-.4a2.5 2.5 0 0 0 1.8-1.8c.4-1.8.4-4.8.4-4.8s0-3-.4-4.8zM10 15.5V8.5l5.5 3.5L10 15.5z"/></svg>`,
  },
];

const { ui, format } = useI18n();
const year = new Date().getFullYear();
const copyright = computed(() => format("footer_copyright", { year }));
</script>

<template>
  <footer v-if="ui" class="site-footer" role="contentinfo">
    <div class="footer-inner">
      <p class="footer-copy">{{ copyright }}</p>
      <div class="footer-social">
        <span class="footer-social-label">{{ ui.footer_follow }}</span>
        <div class="social-links">
          <a
            v-for="link in SOCIAL_LINKS"
            :key="link.id"
            :href="link.url"
            :class="`social-link social-${link.id}`"
            target="_blank"
            rel="noopener noreferrer"
            :aria-label="ui[link.labelKey] || link.id"
            v-html="link.icon"
          />
        </div>
      </div>
    </div>
  </footer>
</template>
