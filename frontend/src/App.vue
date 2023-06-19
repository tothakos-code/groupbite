<template>
  <div class="row d-flex align-items-center">
    <div class="col-7 text-start">
      <div class="align-items-center">
        <h1>Falusi rendelő</h1>
      </div>
    </div>
    <div class="col-5 d-flex ps-0">
      <div class="col-6">
        <button class="btn" id="darkModeToggleButton" onclick="darkModeToggle()">Dark Mode</button>
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
  <div class="row d-flex justify-content-between" style="background-color: rgba(0, 0, 0, 0.2);">
    <span class="col-6 text-start">Készítette: Tóth Ákos</span>
    <span class="col-6 text-end">Verzió: v0.4.1</span>
  </div>
</template>


<script>
import UsernamePopup from './components/UsernamePopup.vue'
import Menu from './components/Menu.vue'
import LocalBasket from './components/LocalBasket.vue'
import GlobalBasket from './components/GlobalBasket.vue'
import * as orginalScript from '../public/scripts.js';
import { socket } from "@/socket";
import { useCookies } from "vue3-cookies";

window.clearBasket = orginalScript.clearBasket;
window.darkModeToggle = orginalScript.darkModeToggle;

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
  methods: {
    onBasketUpdate: function() {
      this.$refs.localbasket.updateBasket();
      socket.emit("Server Basket Update",{ [this.cookies.get('username')]: this.cookies.get('basket') });
    }
  },
  mounted() {
    orginalScript.main();
  }
}
</script>

<style>
</style>
