import { createRouter, createWebHistory } from "vue-router";
const HomeView = () => import("./views/Home.vue");
const AdminHomeView = () => import( "./views/AdminHome.vue");
const MenuView = () => import( "./views/MenuRender.vue");
const AdminSettingsView = () => import( "./views/AdminSettings.vue");
const VendorConfiguration = () => import( "./components/VendorConfiguration.vue");
const AdminVendorsView = () => import( "./views/AdminVendors.vue");
const AdminOrdersView = () => import( "./views/AdminOrders.vue");
const AdminUsersView = () => import( "./views/AdminUsers.vue");
const VendorItemManager = () => import( "./components/VendorItemManager.vue");
const VendorAdd = () => import( "./components/VendorAdd.vue");
const NotFound = () => import( "./components/NotFound.vue");

const routes = [
  {
    path: '/api/:pathMatch(.*)*',
    beforeEnter: () => {
      window.location.href = window.location.pathname
    }
  },
  {
    name: "home",
    path: "/home",
    component: HomeView,
  },
  {
    name: "root",
    path: "/",
    redirect: "/home",
  },
  {
    name: "admin",
    path: "/admin",
    component: AdminHomeView,
    children: [
      {
        name:"settings",
        path: "settings",
        component: AdminSettingsView
      },
      {
        name:"orders",
        path: "orders",
        component: AdminOrdersView
      },
      {
        name:"users",
        path: "users",
        component: AdminUsersView
      },
      {
        name:"vendorlist",
        path: "vendors",
        component: AdminVendorsView
      },
      {
        path: ":id/config",
        component: VendorConfiguration,
      },
      {
        name:"vendorItems",
        path: ":id/config/:menuId",
        component: VendorItemManager
      },
      {
        path: "add",
        component: VendorAdd
      }
    ]
  },
  {
    name: "menu",
    path: "/menu",
    component: MenuView
  },
  {
    name: "NotFound",
    path: "/:pathMatch(.*)*",
    component: NotFound
  },
];
const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes: routes
});

export default router;
