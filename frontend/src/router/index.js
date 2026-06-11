import { createRouter, createWebHistory } from "vue-router";
import CatalogView from "@/views/CatalogView.vue";
import ProductView from "@/views/ProductView.vue";
import OrderView from "@/views/OrderView.vue";
import AboutView from "@/views/AboutView.vue";
import ContactView from "@/views/ContactView.vue";
import AdminView from "@/views/AdminView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "catalog",
      component: CatalogView,
      meta: { active: "catalog", bodyClass: "page-catalog" },
    },
    {
      path: "/catalog/:slug",
      name: "product",
      component: ProductView,
      meta: { active: "catalog", bodyClass: "page-product" },
    },
    {
      path: "/order/:id",
      name: "order",
      component: OrderView,
      meta: { active: "catalog", bodyClass: "page-order", titleKey: null },
    },
    {
      path: "/about",
      name: "about",
      component: AboutView,
      meta: { active: "about", bodyClass: "page-content", titleKey: "about_title" },
    },
    {
      path: "/contact",
      name: "contact",
      component: ContactView,
      meta: { active: "contact", bodyClass: "page-content", titleKey: "contact_title" },
    },
    {
      path: "/admin",
      name: "admin",
      component: AdminView,
      meta: { bodyClass: "page-admin" },
    },
  ],
});

export default router;
