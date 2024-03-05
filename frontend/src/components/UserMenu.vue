<template>
  <div
    v-if="isLoggedIn"
    class="d-flex"
  >
    <div class="btn-group ">
      <button
        type="button"
        class="d-none d-md-inline btn pe-none border border-secondary"
      >
        {{ username }}
      </button>
      <button
        id="dropdownMenuButton1"
        type="button"
        class="btn btn-outline-secondary dropdown-toggle dropdown-toggle-split rounded-sm hide-sm-arrow"
        data-bs-toggle="dropdown"
        aria-expanded="false"
      >
        <span class="d-inline d-md-none">☰</span>
      </button>
      <ul
        class="dropdown-menu"
        aria-labelledby="dropdownMenuButton1"
      >
        <li class="d-inline d-md-none">
          <button
            class="dropdown-item disabled"
            aria-disabled="true"
          >
            <span>
              {{ username }}
            </span>
          </button>
        </li>
        <li class="d-inline d-md-none">
          <hr class="dropdown-divider">
        </li>
        <li class="d-inline d-md-none">
          <UserControllPanel />
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
      </ul>
    </div>
  </div>
  <div v-else>
    <button
      class="btn btn-dark"
      @click="showLogin = true"
    >
      Bejelentkezés
    </button>
  </div>
  <UserProfilePopup
    v-if="isLoggedIn"
    :show="showProfile"
    @cancel="showProfile = false"
  />
  <UserLoginPopup
    :show="showLogin"
    @cancel="showLogin = false"
  />
</template>

<script>
import { state } from "@/socket.js"
import UserProfilePopup from './UserProfilePopup.vue';
import UserLoginPopup from './UserLoginPopup.vue';
import UserControllPanel from './UserControllPanel.vue'

export default {
  name: 'UserMenu',
  components: {
    UserLoginPopup,
    UserControllPanel,
    UserProfilePopup
  },
  data() {
    return {
      showProfile: false,
      showLogin: false
    }
  },
  computed: {
    isLoggedIn() {
      return state.user.id !== undefined;
    },
    username() {
      return state.user.username;
    }
  }
}
</script>

<style>
@media (max-width: 768px) {
     .rounded-sm {
       border-radius: 0.375rem !important;
     }
     .hide-sm-arrow::after {
      display: none !important;
    }
   }
</style>
