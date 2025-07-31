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
          classes=""
        >
          <template #body="props">
            <v-card
              class="notification-card mb-3"
              :class="{
                'bg-warning':props.item.type === 'warn',
                'bg-error':props.item.type === 'error',
                'bg-info-subtle':props.item.type === 'info',
                'bg-warning-subtle':props.item.type === 'warn' && theme === 'dark',
                'bg-danger-subtle':props.item.type === 'error' && theme === 'dark',
              }"
              elevation="8"
              rounded="lg"
              min-width="400"
            >
              <!-- Header Section -->
              <v-card-item class="pb-2">
                <div class="d-flex align-items-start">
                  <!-- Icon Avatar -->
                  <v-avatar
                    size="40"
                    :color="props.item.type === 'success' ? 'success' :
                      props.item.type === 'error' ? 'error' :
                      props.item.type === 'warn' || props.item.type === 'warning' ? 'warning' :
                      props.item.type === 'info' ? 'info' : 'primary'"
                    class="me-3 flex-shrink-0"
                  >
                    <v-icon
                      :icon="props.item.type === 'success' ? 'mdi-check-circle' :
                        props.item.type === 'error' ? 'mdi-alert-circle' :
                        props.item.type === 'warn' || props.item.type === 'warning' ? 'mdi-alert' :
                        props.item.type === 'info' ? 'mdi-information' : 'mdi-bell'"
                      color="white"
                      size="20"
                    />
                  </v-avatar>

                  <!-- Content -->
                  <div class="flex-grow-1">
                    <div class="text-subtitle-1 font-weight-bold notification-title">
                      {{ props.item.title ||
                        (props.item.type === 'success' ? 'Sikeres művelet' :
                          props.item.type === 'error' ? 'Hiba történt' :
                          props.item.type === 'warn' || props.item.type === 'warning' ? 'Figyelmeztetés' :
                          props.item.type === 'info' ? 'Információ' : 'Értesítés') }}
                    </div>
                    <div class="text-caption text-medium-emphasis">
                      {{ new Date().toLocaleTimeString('hu-HU', { hour: '2-digit', minute: '2-digit' }) }}
                    </div>
                  </div>

                  <!-- Close Button -->
                  <v-btn
                    icon="mdi-close"
                    variant="text"
                    size="small"
                    density="comfortable"
                    class="flex-shrink-0 ms-2"
                    @click="props.close"
                  />
                </div>
              </v-card-item>

              <!-- Message Content -->
              <v-card-text class="pt-0 pb-3">
                <div class="text-body-2 notification-message">
                  {{ props.item.text }}
                </div>
              </v-card-text>

              <!-- Progress indicator -->
              <div class="notification-progress-container">
                <v-progress-linear
                  :color="props.item.type === 'success' ? 'success' :
                    props.item.type === 'error' ? 'error' :
                    props.item.type === 'warn' || props.item.type === 'warning' ? 'warning' :
                    props.item.type === 'info' ? 'info' : 'primary'"
                  height="4"
                  indeterminate
                  class="notification-progress"
                />
              </div>
            </v-card>
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
    if (!theme.value) {
      theme.value = "light"
    }
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
