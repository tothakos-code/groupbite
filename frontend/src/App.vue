<template>
  <div class="row">
    <Sidebar />
    <div class="col w-100 pt-2 flex-grow-1 ">
      <div class="row bg-body-secondary d-flex justify-content-between rounded mx-0 px-0 pt-2 pb-2">
        <div class="col-11 col-md-7 row d-flex justify-content-between">
          <div class="col-8 row d-flex justify-content-start align-items-center">
            <h1 class="text-truncate">
              Falusi rendelő
            </h1>
          </div>
          <div class="col-3 d-flex align-items-center d-none">
            <span class="col text-danger fs-5 text-truncate">{{ banner() }}</span>
          </div>
          <div class="col-4 d-flex align-items-center">
            <OrderState class="text-truncate" />
          </div>
        </div>
        <div class="col-1 col-md-5 justify-content-end align-items-center my-auto">
          <div class="row">
            <div class="col-0 d-none col-md-9 d-md-flex">
              <UserControllPanel />
            </div>
            <div class="col col-md-3 d-flex justify-content-end align-items-center">
              <UserMenu @to-history="toHistory()" />
            </div>
          </div>
        </div>
      </div>
      <div
        v-if="isDataLoaded"
        class="row d-flex"
      >
        <div class="col-md-7 col-sm-12">
          <div class="row p-2">
            <div
              v-if="showGlobalMessage"
              class="col col-md-3 d-flex flex-fill justify-content-start align-items-center bg-warning bg-opacity-10 border border-warning rounded mb-2"
            >
              Figyelem! A Dátum választó működése megváltozott. Mostmár a rendelés dátumát állítja, mellyel a hét többi napjára is leadhatod rendelésed előre. Ha másik nap menüjéből szeretnél választani használ alatta a menü választót.
              <i
                class="border border-warning rounded p-1"
                @click="dismissGlobalMessage()"
              >bezár</i>
            </div>
            <Menu
              v-if="showMenu"
              key="0"
            />
            <GlobalBasket class="mt-2 d-md-none" />
            <History
              v-if="showHistroy"
              @close="toMenu()"
            />
          </div>
        </div>
        <div class="my-sticky-container col-12 col-md-5 order-first order-md-last">
          <div class="row p-2 ">
            <LocalBasket />
          </div>
          <div class="row p-2 d-none d-md-flex">
            <GlobalBasket />
          </div>
        </div>
      </div>

      <div
        v-else
        class="row col d-flex justify-content-center align-items-center"
      >
        <div
          class="spinner-border"
          style="width: 3rem; height: 3rem;"
        />
      </div>
    </div>
    <notifications
      position="top center"
      classes="my-custom-class"
    >
      <template #body="props">
        <div class="my-notification">
          <div
            class="toast d-flex align-items-center"
            :class="{
              'bg-warning':props.item.type === 'warn',
              'bg-danger':props.item.type === 'error',
              'bg-info-subtle':props.item.type === 'info',
              'bg-warning-subtle':props.item.type === 'warn' && theme === 'dark',
              'bg-danger-subtle':props.item.type === 'error' && theme === 'dark',
            }"
          >
            <p class="title toast-body">
              {{ props.item.title }}
            </p>
            <div>
              {{ props.item.text }}
            </div>
            <button
              type="button"
              class="btn-close me-2 m-auto"
              aria-label="Close"
              @click="props.close"
            />
          </div>
        </div>
      </template>
    </notifications>
    <div class="footer row mt-auto p-3 bg-body-tertiary">
      <div class="row d-flex justify-content-between text-body-secondary">
        <span class="col text-center">
          Készítette:
          <a
            class="link-secondary"
            target="_blank"
            href="https://www.buymeacoffee.com/tothakos"
          >Tóth Ákos</a>
        </span>
        <span class="col text-center">
          <a
            class="link-secondary"
            target="_blank"
            href="https://github.com/tothakos-code/order-accumulator"
          >Forráskód</a>
        </span>
        <span class="col text-center">
          <a
            class="link-secondary"
            target="_blank"
            href="https://docs.google.com/document/d/1x9Wvp5DPZun5OCcNV1B2limlL940EAX6gm03St_Hw-c/edit?usp=sharing"
          >Felhasználói kézikönyv</a>
        </span>
        <span class="col text-center">
          <a
            class="link-secondary"
            target="_blank"
            :href="'https://github.com/tothakos-code/order-accumulator/releases/tag/' + showVersion()"
          >Változásnapló</a>
        </span>
        <span class="col text-center">Verzió: {{ showVersion() }}</span>
      </div>
    </div>
  </div>
</template>


<script>
import UserMenu from './components/UserMenu.vue'
import Menu from './components/Menu.vue'
import Sidebar from './components/Sidebar.vue'
import History from './components/History.vue'
import LocalBasket from './components/LocalBasket.vue'
import GlobalBasket from './components/GlobalBasket.vue'
import OrderState from './components/OrderState.vue'
import UserControllPanel from './components/UserControllPanel.vue'
import { state, socket } from "@/socket";
// import { useAuth } from "@/auth";
import { useCookies } from "vue3-cookies";
import { provide, ref } from 'vue';
import { notify } from "@kyvg/vue3-notification";




export default {
  name: 'App',
  components: {
    UserMenu,
    UserControllPanel,
    Menu,
    Sidebar,
    History,
    OrderState,
    LocalBasket,
    GlobalBasket
  },
  setup() {
    const { cookies } = useCookies();

    const theme = ref(localStorage.getItem("theme"))
    const userColor = ref(state.user.ui_color)

    function toggleDarkMode() {
      if (theme.value === 'dark') {
        theme.value = 'light'
      } else {
        theme.value = 'dark'
      }
      localStorage.setItem("theme", theme.value);
      socket.emit("User Update", {"id": state.user.id, "ui_theme":this.theme}, function(user) {
        state.user = user;
      });
      document.documentElement.setAttribute('data-bs-theme', theme.value)
    }

    provide('theme', {
      theme,
      toggleDarkMode,
      userColor
    })
    return {
      cookies,
      theme
    };
  },
  data() {
    return {
      showMenu: true,
      showGlobalMessage: false,
      showHistroy: false
    }
  },
  computed: {
    isDataLoaded(){
      return (state.user !== undefined && state.user.ui_color) || !this.$cookies.isKey('username')
    }
  },
  mounted() {
    const userDismissed = localStorage.getItem("gm-date-func-change");
    if (!userDismissed) {
      this.showGlobalMessage = true;
    }

    const currentTheme = localStorage.getItem("theme");
    if (!currentTheme) {
      this.theme = 'light'
    } else {
      this.theme = currentTheme
    }
    localStorage.setItem("theme", this.theme);
    document.documentElement.setAttribute('data-bs-theme', this.theme)
  },
  methods: {
    showVersion: function() {
      // eslint-disable-next-line
      return 'v' + process.env.VUE_APP_VERSION;
    },
    banner: function() {
      // eslint-disable-next-line
      return process.env.VUE_APP_FALU_BANNER;
    },
    toMenu: function() {
      this.showMenu = true;
      this.showHistroy = false;
    },
    toHistory: function() {
      this.showHistroy = true;
      this.showMenu = false;
    },
    dismissGlobalMessage() {
      // Hide the message
      this.showGlobalMessage = false;

      notify({
        type: "info",
        text: "Az üzenet nemfog többet megjelenni."
      });

      // Save in local storage that the user has dismissed the message
      localStorage.setItem("gm-date-func-change", "true");
    },
  }
}
</script>


<style>
@media only screen and (max-width: 768px){
  .my-sticky-container {
        position: sticky;
        top: 5px;
        z-index: 1;
  }
 }


</style>
