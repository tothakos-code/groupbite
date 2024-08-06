<template>
  <div class="row col d-flex min-vh-100 h-auto">
    <Sidebar />
    <div class="col px-0 w-100 flex-grow-1">
      <div class="row col-12 bg-body-secondary d-flex justify-content-between mx-0 px-0">
        <div class="col-7 justify-content-start align-items-center">
          <h3 class="text-truncate">
            GroupBite
          </h3>
        </div>
        <div class="col col-sm-3 d-flex justify-content-end align-items-center">
          <UserMenu />
        </div>
      </div>
      <router-view
        v-slot="{ Component }"
        class="row ps-2 me-0"
      >
        <Transition
          mode="out-in"
        >
          <component
            :is="Component"
          />
        </Transition>
      </router-view>
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
// import { socket } from "@/main";
import { useAuth } from "@/stores/auth";
import { useCookies } from "vue3-cookies";
import { provide, ref } from 'vue';




export default {
  name: 'App',
  components: {
    UserMenu,
    Sidebar,
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
      location.reload();
      // if (this.auth.isLoggedIn) {
      //   socket.emit("User Update", {"id": this.auth.user.id, "ui_theme":this.theme}, function(user) {
      //     this.auth.user = user;
      //   });
      // }
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
  transition: opacity 0.2s ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
}

</style>
