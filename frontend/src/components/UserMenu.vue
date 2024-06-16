<template>
  <button
  class="btn btn-sm me-2"
  :class="{
    'btn-dark':theme === 'light',
    'btn-light':theme === 'dark'
    }"
    @click="toggleDarkMode"
    >
    <svg
    v-if="theme === 'light'"
    xmlns="http://www.w3.org/2000/svg"
    width="16"
    height="16"
    fill="currentColor"
    class="bi bi-moon-fill"
    viewBox="0 0 16 16"
    >
    <path d="M6 .278a.768.768 0 0 1 .08.858 7.208 7.208 0 0 0-.878 3.46c0 4.021 3.278 7.277 7.318 7.277.527 0 1.04-.055 1.533-.16a.787.787 0 0 1 .81.316.733.733 0 0 1-.031.893A8.349 8.349 0 0 1 8.344 16C3.734 16 0 12.286 0 7.71 0 4.266 2.114 1.312 5.124.06A.752.752 0 0 1 6 .278z" />
  </svg>
  <svg
  v-else
  xmlns="http://www.w3.org/2000/svg"
  width="16"
  height="16"
  fill="currentColor"
  class="bi bi-brightness-high-fill"
  viewBox="0 0 16 16"
  >
  <path d="M12 8a4 4 0 1 1-8 0 4 4 0 0 1 8 0zM8 0a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 0zm0 13a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 13zm8-5a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2a.5.5 0 0 1 .5.5zM3 8a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2A.5.5 0 0 1 3 8zm10.657-5.657a.5.5 0 0 1 0 .707l-1.414 1.415a.5.5 0 1 1-.707-.708l1.414-1.414a.5.5 0 0 1 .707 0zm-9.193 9.193a.5.5 0 0 1 0 .707L3.05 13.657a.5.5 0 0 1-.707-.707l1.414-1.414a.5.5 0 0 1 .707 0zm9.193 2.121a.5.5 0 0 1-.707 0l-1.414-1.414a.5.5 0 0 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .707zM4.464 4.465a.5.5 0 0 1-.707 0L2.343 3.05a.5.5 0 1 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .708z" />
</svg>
</button>
  <div
    v-if="auth.isLoggedIn"
    class="d-flex"
  >
    <div class="btn-group fs-5 ">
      <a
        id="dropdownMenuButton1"
        type="button"
        class="text-reset links dropdown-toggle hide-xs-arrow"
        data-bs-toggle="dropdown"
        aria-expanded="false"
      >
        <span class="d-none d-sm-inline pe-1">{{ auth.user.username }}</span>
        <span class="d-inline d-sm-none">☰</span>
      </a>
      <ul
        class="dropdown-menu"
      >
        <li class="d-inline d-md-none">
          <button
            class="dropdown-item disabled"
            aria-disabled="true"
          >
            <span>
              {{ auth.user.username }}
            </span>
          </button>
        </li>
        <li class="d-inline d-md-none">
          <hr class="dropdown-divider">
        </li>
        <li class="d-inline d-md-none">
          <hr class="dropdown-divider">
        </li>
        <li>
          <button
            class="dropdown-item"
            @click="showProfile = true"
          >
            <span>
              Profil beállítások
            </span>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              fill="currentColor"
              class="bi bi-pen"
              viewBox="0 0 16 16"
              data-darkreader-inline-fill=""
              style="--darkreader-inline-fill:currentColor;"
            >
              <path d="m13.498.795.149-.149a1.207 1.207 0 1 1 1.707 1.708l-.149.148a1.5 1.5 0 0 1-.059 2.059L4.854 14.854a.5.5 0 0 1-.233.131l-4 1a.5.5 0 0 1-.606-.606l1-4a.5.5 0 0 1 .131-.232l9.642-9.642a.5.5 0 0 0-.642.056L6.854 4.854a.5.5 0 1 1-.708-.708L9.44.854A1.5 1.5 0 0 1 11.5.796a1.5 1.5 0 0 1 1.998-.001zm-.644.766a.5.5 0 0 0-.707 0L1.95 11.756l-.764 3.057 3.057-.764L14.44 3.854a.5.5 0 0 0 0-.708l-1.585-1.585z" />
            </svg>
          </button>
        </li>
        <li>
          <button class="dropdown-item">
            <span>
              Előző rendelések???
            </span>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              fill="currentColor"
              class="bi bi-clock-history"
              viewBox="0 0 16 16"
            >
              <path d="M8.515 1.019A7 7 0 0 0 8 1V0a8 8 0 0 1 .589.022l-.074.997zm2.004.45a7.003 7.003 0 0 0-.985-.299l.219-.976c.383.086.76.2 1.126.342l-.36.933zm1.37.71a7.01 7.01 0 0 0-.439-.27l.493-.87a8.025 8.025 0 0 1 .979.654l-.615.789a6.996 6.996 0 0 0-.418-.302zm1.834 1.79a6.99 6.99 0 0 0-.653-.796l.724-.69c.27.285.52.59.747.91l-.818.576zm.744 1.352a7.08 7.08 0 0 0-.214-.468l.893-.45a7.976 7.976 0 0 1 .45 1.088l-.95.313a7.023 7.023 0 0 0-.179-.483zm.53 2.507a6.991 6.991 0 0 0-.1-1.025l.985-.17c.067.386.106.778.116 1.17l-1 .025zm-.131 1.538c.033-.17.06-.339.081-.51l.993.123a7.957 7.957 0 0 1-.23 1.155l-.964-.267c.046-.165.086-.332.12-.501zm-.952 2.379c.184-.29.346-.594.486-.908l.914.405c-.16.36-.345.706-.555 1.038l-.845-.535zm-.964 1.205c.122-.122.239-.248.35-.378l.758.653a8.073 8.073 0 0 1-.401.432l-.707-.707z" />
              <path d="M8 1a7 7 0 1 0 4.95 11.95l.707.707A8.001 8.001 0 1 1 8 0v1z" />
              <path d="M7.5 3a.5.5 0 0 1 .5.5v5.21l3.248 1.856a.5.5 0 0 1-.496.868l-3.5-2A.5.5 0 0 1 7 9V3.5a.5.5 0 0 1 .5-.5z" />
            </svg>
          </button>
        </li>
        <li>
          <button
            class="dropdown-item"
            @click="auth.logout()"
          >
            <span>
              Kijelentkezés
            </span>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-box-arrow-right" viewBox="0 0 16 16">
  <path fill-rule="evenodd" d="M10 12.5a.5.5 0 0 1-.5.5h-8a.5.5 0 0 1-.5-.5v-9a.5.5 0 0 1 .5-.5h8a.5.5 0 0 1 .5.5v2a.5.5 0 0 0 1 0v-2A1.5 1.5 0 0 0 9.5 2h-8A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h8a1.5 1.5 0 0 0 1.5-1.5v-2a.5.5 0 0 0-1 0z"/>
  <path fill-rule="evenodd" d="M15.854 8.354a.5.5 0 0 0 0-.708l-3-3a.5.5 0 0 0-.708.708L14.293 7.5H5.5a.5.5 0 0 0 0 1h8.793l-2.147 2.146a.5.5 0 0 0 .708.708z"/>
</svg>
          </button>
        </li>
      </ul>
    </div>
  </div>
  <div v-else>
    <button
      class="btn btn-sm btn-dark"
      @click="showLogin = true"
    >
      Bejelentkezés
    </button>
  </div>
  <UserProfilePopup
    v-if="auth.isLoggedIn"
    :show="showProfile"
    @cancel="showProfile = false"
  />
  <UserLoginPopup
    :show="showLogin"
    @cancel="showLogin = false"
  />
</template>

<script>
import UserProfilePopup from './UserProfilePopup.vue';
import UserLoginPopup from './UserLoginPopup.vue';
import { useAuth } from "@/stores/auth.js";
import { inject } from 'vue';

export default {
  name: 'UserMenu',
  components: {
    UserLoginPopup,
    UserProfilePopup
  },
  setup() {
    const auth = useAuth();
    const { theme, toggleDarkMode } = inject('theme')
    return {
      theme,
      toggleDarkMode,
      auth
    }
  },
  data() {
    return {
      showProfile: false,
      showLogin: false
    }
  },
}
</script>

<style>
@media (max-width: 768px) {
     .rounded-sm {
       border-radius: 0.375rem !important;
     }
   }
@media (max-width: 576px) {
    .hide-xs-arrow::after {
     display: none !important;
   }
  }
.links {
  text-decoration: none;
}
</style>
