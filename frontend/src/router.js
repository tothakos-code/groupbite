import { createRouter, createWebHistory } from 'vue-router';
import HomeView from "./views/Home.vue";
import AdminView from "./views/Admin.vue";
import PluginSettings from "./components/PluginSettings.vue";
import PluginList from "./components/PluginList.vue";
import NotFound from "./components/NotFound.vue";

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
    children: [
      {
        path: '',
        component: PluginList
      },
      {
        path: ':id/config',
        component: PluginSettings
      }
    ]
  },
  {
    name: 'menu',
    path: '/menu',

  },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound },
];
const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes: routes
});

export default router;
