<template>
  <div class="row d-flex align-items-center">
    <div class="col-7 text-start">
      <div class="align-items-center">
        <h1>Falusi rendelő</h1>
      </div>
    </div>
    <div class="col-5 d-flex ps-0 justify-content-start">
        <div class="">
          <button v-if="this.theme === 'light'" class="btn btn-dark ms-2" @click="this.toggleDarkMode()">Dark</button>
          <button v-else class="btn btn-light ms-2" @click="this.toggleDarkMode()">Light</button>
        </div>
        <div v-if="isLoggedIn" class="d-flex justify-content-start">

          <div class="">
            <button v-if="this.subscriptionState != 'full'" type="button" class="btn btn-warning mx-2 position-relative" @click="this.subscribe()">
              Feliratkozás
              <span class="position-absolute top-0 start-50 translate-middle badge rounded-pill bg-danger">
                Leiratkozva
              </span>
            </button>
            <button v-else type="button" class="btn btn-warning mx-2 position-relative" @click="this.unSubscribe()">
              Leiratkozás
              <span class="position-absolute top-0 start-50 translate-middle badge rounded-pill bg-success">
                Feliratkozva
              </span>
            </button>
          </div>
        </div>
      <div class="col text-end d-flex justify-content-end align-items-center">
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
import { state, socket } from "@/socket";
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
    },
    subscribe: function() {
      socket.emit("User Update", {"username": state.user.username, "subscribed":"full"}, function(user) {
        state.user = user;
      });
    },
    unSubscribe: function() {
      socket.emit("User Update", {"username": state.user.username, "subscribed":"none"}, function(user) {
        state.user = user;
      });
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
    subscriptionState() {
      return state.user.subscribed;
    },
    isLoggedIn() {
      return !(state.user === undefined || state.user.username === undefined);
    }
  }
}
</script>

<style>
</style>
