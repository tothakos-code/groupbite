import { createRouter, createWebHistory } from 'vue-router';
import HomeView from "./views/Home.vue";
import AdminView from "./views/Admin.vue";

const routes = [
  {
    name: 'home',
    path: '/home',
    component: HomeView,
  },
  {
    name: 'root',
    path: '/',
    redirect: '/home',
  },
  {
    name: 'admin',
    path: '/admin',
    component: AdminView,
  },
  {
    name: 'menu',
    path: '/menu',

  },
];
const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes: routes
});

export default router;
