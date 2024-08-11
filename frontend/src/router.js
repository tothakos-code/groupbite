import { createRouter, createWebHistory } from "vue-router";
import HomeView from "./views/Home.vue";
import AdminView from "./views/Admin.vue";
import MenuView from "./views/MenuRender.vue";
import VendorConfiguration from "./components/VendorConfiguration.vue";
import VendorList from "./components/VendorList.vue";
import VendorAdd from "./components/VendorAdd.vue";
import NotFound from "./components/NotFound.vue";

const routes = [
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
        name:"vendorlist",
        path: "",
        component: VendorList
      },
      {
        path: ":id/config",
        component: VendorConfiguration,
        // props: true
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
