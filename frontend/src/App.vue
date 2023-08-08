<template>
  <div class="bg-body-secondary d-flex row align-items-center mx-0 px-0 pt-2 pb-2 rounded">
    <div class="col-7 row d-flex">
        <div class="col d-flex justify-content-start align-items-center">
          <h1>Falusi rendelő</h1>
        </div>
        <div class="col d-flex justify-content-end align-items-center">
          <OrderState/>
        </div>
    </div>
    <div class="col-5 d-flex ps-0 justify-content-start align-items-center">
        <div class="">
          <button v-if="this.theme === 'light'" class="btn btn-dark ms-2" @click="this.toggleDarkMode()">Dark</button>
          <button v-else class="btn btn-light ms-2" @click="this.toggleDarkMode()">Light</button>
        </div>
        <div v-if="isLoggedIn" class="d-flex justify-content-start">
          <div class="" title="Ha feliratkozol megjelenik a neved minden nap a közös kosárban. Így a többiek látják, hogy még nem választottál és biztos nem maradsz le a rendelésről.">
            <button v-if="this.subscriptionState != 'full'" type="button" class="btn mx-2 position-relative" :class="['btn-' + this.usercolor ]" @click="this.subscribe()">
              Feliratkozás
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-repeat" viewBox="0 0 16 16">
                <path d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z"/>
                <path fill-rule="evenodd" d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5.002 5.002 0 0 0 8 3zM3.1 9a5.002 5.002 0 0 0 8.757 2.182.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9H3.1z"/>
              </svg>
              <span class="position-absolute top-0 start-50 translate-middle badge rounded-pill bg-danger">
                Leiratkozva
              </span>
            </button>
            <button v-else type="button" class="btn mx-2 position-relative" :class="['btn-' + this.usercolor ]" @click="this.unSubscribe()">
              Leiratkozás
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-repeat" viewBox="0 0 16 16">
                <path d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z"/>
                <path fill-rule="evenodd" d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5.002 5.002 0 0 0 8 3zM3.1 9a5.002 5.002 0 0 0 8.757 2.182.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9H3.1z"/>
                <path fill-rule="evenodd" d="M13.854 2.146a.5.5 0 0 1 0 .708l-11 11a.5.5 0 0 1-.708-.708l11-11a.5.5 0 0 1 .708 0Z"/>
              </svg>
              <span class="position-absolute top-0 start-50 translate-middle badge rounded-pill bg-success">
                Feliratkozva
              </span>
            </button>
          </div>
          <a v-if="this.subscriptionState == 'full'" title="Ha feliratkoztál viszont ma hoztál magadnak ebédet/máshol eszel akkor tudod jelezni, hogy ne várjanak rád. Így kikerül a neved a közös kosárból egy nap erejéig de másnap ugyan úgy megjelensz amíg újra nem jelzed.">
            <button v-if="this.currentUserState == 'skip'" type="button" class="btn focus-ring focus-ring-danger" :class="['btn-' + this.usercolor ]" @click="this.waitForMe('none')">
              Ma nem kérek
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-cart-check" viewBox="0 0 16 16">
                <path d="M11.354 6.354a.5.5 0 0 0-.708-.708L8 8.293 6.854 7.146a.5.5 0 1 0-.708.708l1.5 1.5a.5.5 0 0 0 .708 0l3-3z"/>
                <path d="M.5 1a.5.5 0 0 0 0 1h1.11l.401 1.607 1.498 7.985A.5.5 0 0 0 4 12h1a2 2 0 1 0 0 4 2 2 0 0 0 0-4h7a2 2 0 1 0 0 4 2 2 0 0 0 0-4h1a.5.5 0 0 0 .491-.408l1.5-8A.5.5 0 0 0 14.5 3H2.89l-.405-1.621A.5.5 0 0 0 2 1H.5zm3.915 10L3.102 4h10.796l-1.313 7h-8.17zM6 14a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm7 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"/>
              </svg>
            </button>
            <button v-else type="button" class="btn" :class="['btn-outline-' + this.usercolor ]" @click="this.waitForMe('skip')" >
              Ma nem kérek
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-cart-dash" viewBox="0 0 16 16">
                <path d="M6.5 7a.5.5 0 0 0 0 1h4a.5.5 0 0 0 0-1h-4z"/>
                <path d="M.5 1a.5.5 0 0 0 0 1h1.11l.401 1.607 1.498 7.985A.5.5 0 0 0 4 12h1a2 2 0 1 0 0 4 2 2 0 0 0 0-4h7a2 2 0 1 0 0 4 2 2 0 0 0 0-4h1a.5.5 0 0 0 .491-.408l1.5-8A.5.5 0 0 0 14.5 3H2.89l-.405-1.621A.5.5 0 0 0 2 1H.5zm3.915 10L3.102 4h10.796l-1.313 7h-8.17zM6 14a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm7 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"/>
              </svg>
            </button>
          </a>
          <div v-if="this.currentUserState != 'skip'" title="Ha az étel címe nem győzött meg és szeretnél róla videót is látni ezzel a gombal jelezheted. Ekkor bekerül a neved a közös kosára és biztos, hogy nem maradsz le az rendelésről. ">
            <button v-if="this.currentUserState == 'video'" type="button" class="btn btn-primary mx-2" @click="this.waitForMe('none')">
              Videóra várok
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-video3" viewBox="0 0 16 16">
                <path d="M14 9.5a2 2 0 1 1-4 0 2 2 0 0 1 4 0Zm-6 5.7c0 .8.8.8.8.8h6.4s.8 0 .8-.8-.8-3.2-4-3.2-4 2.4-4 3.2Z"/>
                <path d="M2 2a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h5.243c.122-.326.295-.668.526-1H2a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v7.81c.353.23.656.496.91.783.059-.187.09-.386.09-.593V4a2 2 0 0 0-2-2H2Z"/>
              </svg>
            </button>
            <button v-else type="button" class="btn mx-2" :class="['btn-outline-' + this.usercolor ]" @click="this.waitForMe('video')">
              Videóra várok
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-video3" viewBox="0 0 16 16">
                <path d="M14 9.5a2 2 0 1 1-4 0 2 2 0 0 1 4 0Zm-6 5.7c0 .8.8.8.8.8h6.4s.8 0 .8-.8-.8-3.2-4-3.2-4 2.4-4 3.2Z"/>
                <path d="M2 2a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h5.243c.122-.326.295-.668.526-1H2a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v7.81c.353.23.656.496.91.783.059-.187.09-.386.09-.593V4a2 2 0 0 0-2-2H2Z"/>
                <path fill-rule="evenodd" d="M13.854 2.146a.5.5 0 0 1 0 .708l-11 11a.5.5 0 0 1-.708-.708l11-11a.5.5 0 0 1 .708 0Z"/>
              </svg>
            </button>
          </div>
        </div>
      <div class="col text-end d-flex justify-content-end align-items-center">
          <UserMenu @toHistory="toHistory()"/>
      </div>
    </div>
  </div>
  <div class="row d-flex">
    <div class="col-7">
      <div class="row p-2">
        <Menu v-if="this.showMenu"/>
        <History v-if="this.showHistroy" @close="this.toMenu()"/>
      </div>
    </div>
    <div class="col-5">
      <div class="row p-2">
        <LocalBasket/>
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
        Forrás kód: <a class="link-secondary" target="_blank" href="https://github.com/tothakos-code/order-accumulator">Github</a>
      </span>
      <span class="col-3 text-center">
        Változás napló: <a class="link-secondary" target="_blank" :href="'https://github.com/tothakos-code/order-accumulator/releases/tag/' + showVersion()">Jegyzet</a>
      </span>
      <span class="col-3 text-center">Verzió: {{ showVersion() }}</span>
    </div>
  </div>
</template>


<script>
import version from "../package.json";
import UserMenu from './components/UserMenu.vue'
import Menu from './components/Menu.vue'
import History from './components/History.vue'
import LocalBasket from './components/LocalBasket.vue'
import GlobalBasket from './components/GlobalBasket.vue'
import OrderState from './components/OrderState.vue'
import { state, socket } from "@/socket";
import { useCookies } from "vue3-cookies";
// import { Tooltip } from 'bootstrap';


export default {
  name: 'App',
  components: {
    UserMenu,
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
      theme: localStorage.getItem("theme") || 'dark',
      showMenu: true,
      showHistroy: false
    }
  },
  methods: {
    showVersion: function() {
      return 'v' + version.version
    },
    toMenu: function() {
      this.showMenu = true;
      this.showHistroy = false;
    },
    toHistory: function() {
      this.showHistroy = true;
      this.showMenu = false;
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
    },
    waitForMe: function(waitType) {
      if (waitType === 'skip') {
        if ( state.orderState === 'closed') {
          alert("A rendelés már el lett küldve.")
          return;
        }
        // Remove the basket cookie
        state.localBasket = {};
      }
      socket.emit("User Daily State Change",{ 'username': state.user.username, 'new_state':waitType });
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

    // new Tooltip(document.body, {
    //   selector: "[data-bs-toggle='tooltip']",
    // });
  },
  computed: {
    subscriptionState() {
      return state.user.subscribed;
    },
    isLoggedIn() {
      return !(state.user === undefined || state.user.username === undefined);
    },
    currentUserState() {
      return state.userStates[state.user.username];
    },
    usercolor() {
      return state.user.ui_color ? state.user.ui_color : "falusi";
    }
  }
}
</script>


<style>

</style>
