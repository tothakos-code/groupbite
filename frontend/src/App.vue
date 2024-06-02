<template>
  <div class="row col d-flex min-vh-100 h-auto">
    <Sidebar />
    <div class="col px-0 w-100 flex-grow-1">
      <div class="row bg-body-secondary d-flex justify-content-between mx-0 px-0">
        <div class="col-11 col-md-7 row d-flex justify-content-between">
          <div class="col-8 row d-flex justify-content-start align-items-center">
            <h3 class="text-truncate">
              GroupBite
            </h3>
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
              <UserMenu />
            </div>
          </div>
        </div>
      </div>
      <Transition>
        <router-view class="row ps-2 me-0" />
      </Transition>
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
  </div>
</template>


<script>
import UserMenu from './components/UserMenu.vue'
import Sidebar from './components/Sidebar.vue'
import OrderState from './components/OrderState.vue'
import UserControllPanel from './components/UserControllPanel.vue'
import { socket } from "@/socket";
import { useAuth } from "@/stores/auth";
import { useCookies } from "vue3-cookies";
import { provide, ref } from 'vue';
import { notify } from "@kyvg/vue3-notification";




export default {
  name: 'App',
  components: {
    UserMenu,
    UserControllPanel,
    Sidebar,
    OrderState,
  },
  setup() {
    const { cookies } = useCookies();
    const auth = useAuth();
    const theme = ref(localStorage.getItem("theme"));

    auth.checkSession();

    function toggleDarkMode() {
      if (theme.value === 'dark') {
        theme.value = 'light'
      } else {
        theme.value = 'dark'
      }
      localStorage.setItem("theme", theme.value);
      socket.emit("User Update", {"id": this.auth.user.id, "ui_theme":this.theme}, function(user) {
        this.auth.user = user;
      });
      document.documentElement.setAttribute('data-bs-theme', theme.value)
    }

    provide('theme', {
      theme,
      toggleDarkMode,
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
      return (this.auth.user !== undefined && this.auth.user.ui_color) || !this.$cookies.isKey('username')
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
    banner: function() {
      // eslint-disable-next-line
      return process.env.VUE_APP_FALU_BANNER;
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

 .v-enter-active,
 .v-leave-active {
   transition: opacity 0.5s ease;
 }

 .v-enter-from,
 .v-leave-to {
   opacity: 0;
 }

</style>
