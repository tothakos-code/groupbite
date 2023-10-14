<template>
  <div class="col">
    <div class="row bg-body-secondary d-flex justify-content-between rounded mx-0 px-0 pt-2 pb-2">
      <div class="col-11 col-md-7 row d-flex justify-content-between">
          <div class="col-8 row d-flex justify-content-start align-items-center">
              <h1 class="text-truncate">Falusi rendelő</h1>
          </div>
          <div class="col-3 d-flex align-items-center d-none">
            <span class="col text-danger fs-5 text-truncate">{{ this.banner() }}</span>
          </div>
          <div class="col-4 d-flex align-items-center">
            <OrderState class="text-truncate"/>
          </div>
      </div>
      <div class="col-1 col-md-5 justify-content-end align-items-center my-auto">
        <div class="row">
          <div class="col-0 d-none col-md-9 d-md-flex">
            <UserControllPanel/>
          </div>
          <div class="col col-md-3 d-flex justify-content-end align-items-center">
            <UserMenu @toHistory="toHistory()"/>
          </div>
        </div>
      </div>
    </div>
    <div v-if="this.isDataLoaded" class="row d-flex">
      <div class="col-md-7 col-sm-12">
        <div class="row p-2">
          <Menu v-if="this.showMenu" key="0"/>
          <GlobalBasket class="mt-2 d-md-none"/>
          <History v-if="this.showHistroy" @close="this.toMenu()"/>
        </div>
      </div>
      <div class="my-sticky-container col-12 col-md-5 order-first order-md-last">
        <div class="row p-2 ">
          <LocalBasket/>
        </div>
        <div class="row p-2 d-none d-md-flex">
          <GlobalBasket/>
        </div>
      </div>
    </div>

    <div v-else class="row col d-flex justify-content-center align-items-center">
      <div class="spinner-border" style="width: 3rem; height: 3rem;">

      </div>
    </div>
  </div>
  <div class="footer row mt-auto p-3 bg-body-tertiary">
    <div class="row d-flex justify-content-between text-body-secondary">
      <span class="col text-center">Készítette: Tóth Ákos</span>
      <span class="col text-center">
        <a class="link-secondary" target="_blank" href="https://github.com/tothakos-code/order-accumulator">Forráskód</a>
      </span>
      <span class="col text-center">
        <a class="link-secondary" target="_blank" href="#">Felhasználói kézikönyv</a>
      </span>
      <span class="col text-center">
        <a class="link-secondary" target="_blank" :href="'https://github.com/tothakos-code/order-accumulator/releases/tag/' + showVersion()">Változásnapló</a>
      </span>
      <span class="col text-center">Verzió: {{ showVersion() }}</span>
    </div>
  </div>
</template>


<script>
import UserMenu from './components/UserMenu.vue'
import Menu from './components/Menu.vue'
import History from './components/History.vue'
import LocalBasket from './components/LocalBasket.vue'
import GlobalBasket from './components/GlobalBasket.vue'
import OrderState from './components/OrderState.vue'
import UserControllPanel from './components/UserControllPanel.vue'
import { state } from "@/socket";
import { useCookies } from "vue3-cookies";
// import { Tooltip } from 'bootstrap';


export default {
  name: 'App',
  components: {
    UserMenu,
    UserControllPanel,
    Menu,
    History,
    OrderState,
    LocalBasket,
    GlobalBasket
  },
  setup() {
    const { cookies } = useCookies();
    return { cookies };
  },
  data() {
    return {
      showMenu: true,
      showHistroy: false
    }
  },
  methods: {
    showVersion: function() {
      return 'v' + process.env.VUE_APP_VERSION;
    },
    banner: function() {
      return process.env.VUE_APP_FALU_BANNER;
    },
    toMenu: function() {
      this.showMenu = true;
      this.showHistroy = false;
    },
    toHistory: function() {
      this.showHistroy = true;
      this.showMenu = false;
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
  },
  computed: {
    isDataLoaded(){
      return (state.user !== undefined && state.user.ui_color) || !this.$cookies.isKey('username')
    }
  }
}
</script>


<style>
@media only screen and (max-width: 768px){
  .my-sticky-container {
        position: sticky;
        top: 10px;
        z-index: 1;
  }
 }


</style>
