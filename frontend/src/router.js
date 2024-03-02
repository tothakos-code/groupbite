import { createRouter, createWebHistory } from 'vue-router';
import HomeComponent from "./components/HomeComponent.vue";
import AdminView from "./views/Admin.vue";

const routes = [
  {
    name: 'home',
    path: '/home',
    component: HomeComponent,
    params: {
      id: 'home'
    }
  },
  {
    name: 'root',
    path: '/',
    redirect: '/home',
    component: HomeComponent,
    params: {
      id: 'home'
    }
  },
  {
    name: 'admin',
    path: '/admin',
    component: AdminView,
  },
];
const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes: routes
});

export default router;
