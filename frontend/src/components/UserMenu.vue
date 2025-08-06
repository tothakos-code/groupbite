<template>
  <div class="d-flex align-center ga-2">
    <!-- Theme Toggle Button -->
    <v-btn
      :icon="theme === 'light' ? 'mdi-weather-night' : 'mdi-white-balance-sunny'"
      variant="text"
      size="small"
      :title="theme === 'light' ? 'Váltás sötét témára' : 'Váltás világos témára'"
      @click="toggleDarkMode"
    />

    <!-- User Menu (when logged in) -->
    <div v-if="auth.isLoggedIn">
      <v-menu
        v-model="showUserMenu"
        location="bottom end"
        :close-on-content-click="false"
      >
        <template #activator="{ props }">
          <v-btn
            v-bind="props"
            variant="text"
            class="text-none"
            :ripple="false"
          >
            <v-avatar
              size="32"
              :color="theme === 'light' ? 'primary' : 'surface-variant'"
              class="me-2"
            >
              <span class="text-caption font-weight-medium">
                {{ getUserInitials(auth.user.username) }}
              </span>
            </v-avatar>
            <span
              class="d-none d-sm-inline text-truncate"
              style="max-width: 120px;"
            >
              {{ auth.user.username }}
            </span>
            <v-icon
              size="small"
              class="ms-1"
            >
              mdi-chevron-down
            </v-icon>
          </v-btn>
        </template>

        <v-card
          min-width="280"
          elevation="8"
        >
          <!-- User Info Header -->
          <v-card-item class="pb-2">
            <div class="d-flex align-center">
              <v-avatar
                size="40"
                :color="theme === 'light' ? 'primary' : 'surface-variant'"
                class="me-3"
              >
                <span class="text-body-2 font-weight-medium">
                  {{ getUserInitials(auth.user.username) }}
                </span>
              </v-avatar>
              <div>
                <div class="text-body-1 font-weight-medium">
                  {{ auth.user.username }}
                </div>
                <div class="text-caption text-medium-emphasis">
                  Bejelentkezve
                </div>
              </div>
            </div>
          </v-card-item>

          <v-divider />

          <!-- Menu Items -->
          <v-list
            density="comfortable"
            nav
          >
            <v-list-item
              prepend-icon="mdi-account-edit"
              title="Profil beállítások"
              @click="handleProfileClick"
            />

            <v-list-item
              prepend-icon="mdi-clock-time-four"
              title="Rendeléseim"
              @click="handleHistoryClick"
            />

            <v-list-item
              v-if="auth.user.admin"
              prepend-icon="mdi-cog"
              title="Adminisztráció"
              @click="handleAdminClick"
            />

            <v-divider class="my-1" />

            <v-list-item
              prepend-icon="mdi-logout"
              title="Kijelentkezés"
              class="text-error"
              @click="handleLogoutClick"
            />
          </v-list>
        </v-card>
      </v-menu>
    </div>

    <!-- Login Button (when not logged in) -->
    <div v-else>
      <v-btn
        color="primary"
        variant="elevated"
        size="small"
        prepend-icon="mdi-login"
        @click="showLogin = true"
      >
        Bejelentkezés
      </v-btn>
    </div>

    <!-- Dialogs -->
    <UserLoginPopup
      v-model="showLogin"
      @cancel="showLogin = false"
    />

    <UserProfilePopup
      v-if="auth.isLoggedIn"
      v-model="showProfile"
      @cancel="showProfile = false"
    />
  </div>
</template>

<script>
import UserProfilePopup from "./UserProfilePopup.vue";
import UserLoginPopup from "./UserLoginPopup.vue";
import { useAuth } from "@/stores/auth.js";
import { inject } from "vue";

export default {
  name: "UserMenu",

  components: {
    UserLoginPopup,
    UserProfilePopup,
  },

  setup() {
    const auth = useAuth();
    const { theme, toggleDarkMode } = inject("theme");

    return {
      theme,
      toggleDarkMode,
      auth
    };
  },

  data() {
    return {
      showProfile: false,
      showLogin: false,
      showUserMenu: false,
    };
  },

  methods: {
    getUserInitials(username) {
      if (!username) return '?';
      return username
        .split(' ')
        .map(name => name.charAt(0))
        .join('')
        .substring(0, 2)
        .toUpperCase();
    },

    closeUserMenu() {
      this.showUserMenu = false;
    },

    handleProfileClick() {
      this.showProfile = true;
      this.closeUserMenu();
    },

    handleHistoryClick() {
      this.navigateToHistoryPage();
      this.closeUserMenu();
    },

    handleAdminClick() {
      this.navigateToAdminPage();
      this.closeUserMenu();
    },

    handleLogoutClick() {
      this.auth.logout();
      this.closeUserMenu();
    },

    navigateToHistoryPage() {
      this.$router.push({ path: '/history' });
    },

    navigateToAdminPage() {
      this.$router.push({ path: '/admin' });
    },
  }
};
</script>

<style scoped>
.v-btn {
  text-transform: none;
}

.v-list-item.text-error .v-list-item__prepend > .v-icon {
  color: rgb(var(--v-theme-error));
}
</style>
