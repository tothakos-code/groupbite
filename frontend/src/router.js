import { createRouter, createWebHistory } from "vue-router";
const HomeView = () => import("./views/Home.vue");
// const DashboardView = () => import("./views/dashboard/Dashboard.vue");
const AdminHomeView = () => import("./views/admin/AdminHome.vue");
const MenuView = () => import("./views/menu/MenuRender.vue");
const MenuLoading = () => import("./views/menu//MenuLoading.vue");
const AdminSettingsView = () => import("./views/admin/AdminSettings.vue");
const VendorSettings = () => import("./views/admin/vendor/VendorSettings.vue");
const VendorMenuManager = () =>
  import("./views/admin/vendor/VendorMenuManager.vue");
const AdminVendorsView = () => import("./views/admin/AdminVendors.vue");
const AdminOrdersView = () => import("./views/admin/AdminOrders.vue");
const AdminUsersView = () => import("./views/admin/AdminUsers.vue");
const VendorItemManager = () =>
  import("./views/admin/vendor/VendorItemManager.vue");
const VendorAdd = () => import("./components/VendorAdd.vue");
const OrderHistoryView = () => import("./views/history/OrderHistory.vue");
const VendorStatsView = () => import("./components/VendorStats.vue");
const NotFound = () => import("./components/NotFound.vue");
import { useAuth } from "@/stores/auth.js";
import { useVendorStore } from "@/stores/vendor.js";
import { watch } from "vue";

const authGuard = async (to, from, next) => {
  if (!useAuth().user) {
    await useAuth().checkSession();
    if (!useAuth().isLoading && !useAuth().user?.admin) {
      console.log("Nono, you can't do that");
      return false;
    }
  } else if (!useAuth().user?.admin) {
    console.log("Nono, you can't do that");
    return false;
  }
  console.log("Success: admin");
  next();
};

const routes = [
  {
    path: "/api/:pathMatch(.*)*",
    beforeEnter: () => {
      window.location.href = window.location.pathname;
    },
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
    beforeEnter: authGuard,
    children: [
      {
        name: "settings",
        path: "settings",
        component: AdminSettingsView,
      },
      {
        name: "orders",
        path: "orders",
        component: AdminOrdersView,
      },
      {
        name: "users",
        path: "users",
        component: AdminUsersView,
      },
      {
        name: "vendorlist",
        path: "vendors",
        component: AdminVendorsView,
      },
      {
        path: ":id/config",
        component: VendorSettings,
      },
      {
        path: ":id/menu",
        component: VendorMenuManager,
      },
      {
        name: "vendorItems",
        path: ":id/menu/:menuId",
        component: VendorItemManager,
      },
      {
        path: "add",
        component: VendorAdd,
      },
    ],
  },
  {
    name: "menu",
    path: "/menu",
    component: MenuView,
  },
  {
    name: "menu-loading",
    path: "/menu/:rest(.*)*",
    component: MenuLoading,
  },
  {
    name: "history",
    path: "/history",
    beforeEnter: async (to, from, next) => {
      if (!useAuth().user) {
        await useAuth().checkSession();
        if (!useAuth().isLoading && !useAuth().isLoggedIn) {
          console.log("Nono, you can't do that");
          return next({ name: "home" });
        }
      }
      next();
    },
    component: OrderHistoryView,
  },
  {
    name: "stats",
    path: "/stats",
    component: VendorStatsView,
  },
  {
    name: "NotFound",
    path: "/:pathMatch(.*)*",
    component: NotFound,
  },
];
const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes: routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0, left: 0, behavior: "smooth" };
    }
  },
});

router.beforeEach((to, from, next) => {
  const vendorStore = useVendorStore();
  if (vendorStore.routesLoaded) {
    next();
  } else {
    const stopWatching = watch(
      () => vendorStore.routesLoaded,
      (newValue) => {
        if (newValue) {
          stopWatching();
          next();
        }
      },
    );
  }
});

export default router;
