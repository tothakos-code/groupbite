import { createRouter, createWebHistory } from "vue-router";
const HomeView = () => import("./views/Home.vue");
const AdminHomeView = () => import( "./views/admin/AdminHome.vue");
const MenuView = () => import( "./views/menu/MenuRender.vue");
const AdminSettingsView = () => import( "./views/admin/AdminSettings.vue");
const VendorSettings = () => import( "./views/admin/vendor/VendorSettings.vue");
const VendorMenuManager = () => import( "./views/admin/vendor/VendorMenuManager.vue");
const AdminVendorsView = () => import( "./views/admin/AdminVendors.vue");
const AdminOrdersView = () => import( "./views/admin/AdminOrders.vue");
const AdminUsersView = () => import( "./views/admin/AdminUsers.vue");
const VendorItemManager = () => import( "./views/admin/vendor/VendorItemManager.vue");
const VendorAdd = () => import( "./components/VendorAdd.vue");
const NotFound = () => import( "./components/NotFound.vue");
import { useAuth } from "@/stores/auth.js";
import { useVendorStore } from "@/stores/vendor.js";
import { watch } from 'vue';

const authGuard = async (to, from, next) => {
  if (!useAuth().user) {
    await useAuth().checkSession();
      if (!useAuth().isLoading && !useAuth().user?.admin) {
        console.log("Nono, you can't do that");
        return false
      }
    } else if (!useAuth().user?.admin) {
    console.log("Nono, you can't do that");
    return false
  }
  console.log("Success: admin");
  next();
}

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
    beforeEnter: authGuard,
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
        component: VendorSettings,
      },
      {
        path: ":id/menu",
        component: VendorMenuManager,
      },
      {
        name:"vendorItems",
        path: ":id/menu/:menuId",
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

router.beforeEach((to, from, next) => {

  const vendorStore = useVendorStore();
  if (vendorStore.routesLoaded) {
    next()
  } else {
    const stopWatching = watch(() => vendorStore.routesLoaded, (newValue) => {
      if (newValue) {
        stopWatching(); // Stop watching to prevent memory leaks
        next();
      }
    });
  }
});

export default router;
