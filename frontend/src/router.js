import { createRouter, createWebHistory } from "vue-router";
import HomeView from "./views/Home.vue";
import AdminView from "./views/Admin.vue";
import MenuView from "./views/MenuRender.vue";
import Settings from "./views/Settings.vue";
import VendorConfiguration from "./components/VendorConfiguration.vue";
import VendorList from "./components/VendorList.vue";
import VendorItemManager from "./components/VendorItemManager.vue";
import VendorAdd from "./components/VendorAdd.vue";
import NotFound from "./components/NotFound.vue";

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
    component: AdminView,
    children: [
      {
        name:"settings",
        path: "settings",
        component: Settings
      },
      {
        name:"vendorlist",
        path: "",
        component: VendorList
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
