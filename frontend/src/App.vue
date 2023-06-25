<template>
  <div class="row d-flex align-items-center">
    <div class="col-7 text-start">
      <div class="align-items-center">
        <h1>Falusi rendelő</h1>
      </div>
    </div>
    <div class="col-5 d-flex ps-0">
      <div class="col-6">
        <button v-if="this.theme === 'light'" class="btn btn-dark ms-2" @click="this.toggleDarkMode()">Dark</button>
        <button v-else class="btn btn-light ms-2" @click="this.toggleDarkMode()">Light</button>
      </div>
      <div class="col-6 text-end d-flex justify-content-end align-items-center">
          <UsernamePopup/>
      </div>
    </div>
  </div>
  <div class="row d-flex">
    <div class="col-7">
      <div class="row p-2">
        <Menu @basketUpdate="this.onBasketUpdate()"/>
      </div>
    </div>
    <div class="col-5">
      <div class="row p-2">
        <LocalBasket ref="localbasket" @basketUpdate="this.onBasketUpdate()"/>
      </div>
      <div class="row p-2">
        <GlobalBasket/>
      </div>
    </div>
  </div>
  <div class="footer row mt-auto p-3 bg-body-tertiary">
    <div class="row d-flex justify-content-between text-body-secondary">
      <span class="col-3 text-center">Készítette: Tóth Ákos</span>
      <span class="col-3 text-center">
        Forrás kód: <a class="link-secondary" href="https://github.com/tothakos-code/order-accumulator">Github</a>
      </span>
      <span class="col-3 text-center">
        Változás napló: <a class="link-secondary" href="https://github.com/tothakos-code/order-accumulator/releases/tag/v0.4.1">Jegyzet</a>
      </span>
      <span class="col-3 text-center">Verzió: v1.0.0</span>
    </div>
  </div>
</template>


<script>
import UsernamePopup from './components/UsernamePopup.vue'
import Menu from './components/Menu.vue'
import LocalBasket from './components/LocalBasket.vue'
import GlobalBasket from './components/GlobalBasket.vue'
import { socket } from "@/socket";
import { useCookies } from "vue3-cookies";


export default {
  name: 'App',
  components: {
    UsernamePopup,
    Menu,
    LocalBasket,
    GlobalBasket
  },
  setup() {
    const { cookies } = useCookies();
    return { cookies };
  },
  data() {
    return {
      theme: localStorage.getItem("theme") || 'dark'
    }
  },
  methods: {
    onBasketUpdate: function() {
      this.$refs.localbasket.updateBasket();
      socket.emit("Server Basket Update",{ [this.cookies.get('username')]: this.cookies.get('basket') });
    },
    toggleDarkMode: function() {
      if (this.theme === 'dark') {
        this.theme = 'light'
      } else {
        this.theme = 'dark'
      }
      localStorage.setItem("theme", this.theme);
      document.documentElement.setAttribute('data-bs-theme', this.theme)
    }
  },
  mounted() {
    const currentTheme = localStorage.getItem("theme");
    if (!currentTheme) {
      this.theme = 'light'
    } else {
      this.theme = currentTheme
    }
    localStorage.setItem("theme", this.theme);
    document.documentElement.setAttribute('data-bs-theme', this.theme)
  }
}
</script>

<style>
</style>
