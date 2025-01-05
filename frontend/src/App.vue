<template>
  <v-app id="inspire">
    <v-theme-provider>
      <v-navigation-drawer
        v-model="drawer"
        class="bg-primary"
        rail
        mobile-breakpoint="sm"
      >
        <Sidebar />
        <template #append>
          <VersionInfo class=" d-flex flex-fill p-0 align-items-end justify-content-center mb-2" />
        </template>
      </v-navigation-drawer>
      <v-main>
        <v-app-bar
          height="45"
          scroll-behavior="hide"
        >
          <v-app-bar-nav-icon
            v-show="!smAndUp"
            variant="text"
            @click.stop="drawer = !drawer"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              fill="currentColor"
              class="bi bi-layout-sidebar"
              viewBox="0 0 16 16"
            >
              <path d="M0 3a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2zm5-1v12h9a1 1 0 0 0 1-1V3a1 1 0 0 0-1-1zM4 2H2a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h2z" />
            </svg>
          </v-app-bar-nav-icon>
          <v-app-bar-title>{{ app_title }}</v-app-bar-title>
          <v-spacer />
          <UserMenu />
        </v-app-bar>
        <router-view
          v-slot="{ Component }"
        >
          <Transition
            mode="out-in"
          >
            <component
              :is="Component"
            />
          </Transition>
        </router-view>
        <notifications
          position="top center"
          :ignore-duplicates="true"
          :pause-on-hover="true"
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
      </v-main>
    </v-theme-provider>
  </v-app>
</template>


<script>
import UserMenu from "./components/UserMenu.vue"
import Sidebar from "./components/Sidebar.vue"
import VersionInfo from "@/components/VersionInfo.vue"
import axios from "axios";
import { useAuth } from "@/stores/auth";
import { useCookies } from "vue3-cookies";
import { provide, ref } from "vue";
import { useTheme } from 'vuetify'
import { useDisplay } from 'vuetify'

export default {
  name: "App",
  components: {
    UserMenu,
    Sidebar,
    VersionInfo
  },
  setup() {
    const { cookies } = useCookies();
    const auth = useAuth();
    const theme = ref(localStorage.getItem("theme"));
    const Vtheme = useTheme()
    const { smAndUp } = useDisplay();
    Vtheme.global.name.value = theme.value
    auth.checkSession();

    function toggleDarkMode() {
      if (theme.value === "dark") {
        theme.value = "light"
        Vtheme.global.name.value = 'light'
      } else {
        theme.value = "dark"
        Vtheme.global.name.value = 'dark'
      }
      localStorage.setItem("theme", theme.value);
      document.documentElement.setAttribute("data-bs-theme", theme.value)
    }

    provide("theme", {
      theme,
      toggleDarkMode,
    })
    return {
      cookies,
      theme,
      auth,
      smAndUp
    };
  },
  data() {
    return {
      showMenu: true,
      showGlobalMessage: false,
      showHistroy: false,
      app_title: "",
      drawer: true,
    }
  },
  computed: {
    isDataLoaded(){
      return (this.auth.user !== undefined && this.auth.user.ui_color) || !this.$cookies.isKey("username")
    }
  },
  mounted() {
    axios.get(`http://${window.location.host}/api/setting/get/app_title`)
      .then(response => {
        this.app_title = response.data.app_title;
      })
      .catch(e => {
          console.log(e);
          this.app_title = "GroupBite";
      })

    const currentTheme = localStorage.getItem("theme");
    if (!currentTheme) {
      this.theme = "light"
    } else {
      this.theme = currentTheme
    }
    localStorage.setItem("theme", this.theme);
    document.documentElement.setAttribute("data-bs-theme", this.theme)
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
