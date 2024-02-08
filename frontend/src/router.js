import { createRouter, createWebHistory } from 'vue-router';
import HomeComponent from "./components/HomeComponent.vue";
import HomeTwoComponent from "./components/HomeTwoComponent.vue";

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
    name: 'home2',
    path: '/home2',
    component: HomeTwoComponent,
    props: {
      id: 'home2'
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
];
const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes: routes
});
router.beforeEach((to, from) => {
  console.log({to, from})
})
export default router;
