import { createApp } from 'vue';
import App from './App.vue';
import VueCookies from 'vue3-cookies';

let app = createApp(App);
app.use(VueCookies);
app.mount('#app');
