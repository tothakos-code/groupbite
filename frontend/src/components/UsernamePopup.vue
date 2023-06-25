<template>
  <div v-if="isLoggedIn"  class="d-flex">
    <div class="btn-group mb-3">
      <button type="button" class="btn btn-outline-warning disabled" disabled>{{ username }}</button>
      <button type="button" class="btn btn-outline-warning dropdown-toggle dropdown-toggle-split" data-bs-toggle="dropdown" aria-expanded="false">
        <span class="visually-hidden">Toggle Dropdown</span>
      </button>
      <ul class="dropdown-menu">
        <li>
          <a class="dropdown-item" @click="showProfile = true" href="#">
            <span>
              Név szerkesztése
            </span>
            <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" fill="currentColor" class="bi bi-pen mt-1" viewBox="0 0 16 16" data-darkreader-inline-fill="" style="--darkreader-inline-fill:currentColor;">
              <path d="m13.498.795.149-.149a1.207 1.207 0 1 1 1.707 1.708l-.149.148a1.5 1.5 0 0 1-.059 2.059L4.854 14.854a.5.5 0 0 1-.233.131l-4 1a.5.5 0 0 1-.606-.606l1-4a.5.5 0 0 1 .131-.232l9.642-9.642a.5.5 0 0 0-.642.056L6.854 4.854a.5.5 0 1 1-.708-.708L9.44.854A1.5 1.5 0 0 1 11.5.796a1.5 1.5 0 0 1 1.998-.001zm-.644.766a.5.5 0 0 0-.707 0L1.95 11.756l-.764 3.057 3.057-.764L14.44 3.854a.5.5 0 0 0 0-.708l-1.585-1.585z"></path>
            </svg>
          </a>
        </li>
      </ul>
    </div>
  </div>
  <div v-else class="">
    <button @click="showProfile = true" class="btn btn-dark">Bejelentkezés</button>
  </div>
  <Popup  :showModal="showProfile" title="Név választás" @cancel="showProfile = false" @confirm="this.saveUsername()">
    <p>Egy név ami alapján beazonosíthatnak téged.</p>
    <p>Nincs külön regisztráció. A név megadásával már létre is jön a fiókod.</p>
    <p>A fiókodba belépni későb a neved megadásával tudsz.</p>
    <div class="input-group mb-3">
      <span class="input-group-text" id="basic-addon1">Név</span>
      <input type="text" v-model.trim="username" class="form-control" placeholder="Username" aria-label="Username" aria-describedby="basic-addon1">
    </div>
  </Popup>
</template>

<script>
import Popup from './Popup.vue';
import { useCookies } from "vue3-cookies";
import { state, socket } from "@/socket";

export default {
  name: 'UsernamePopup',
  components: {
    Popup
  },
  setup() {
    const { cookies } = useCookies();
    return { cookies };
  },
  mounted() {
    if (this.$cookies.isKey('username')) {
      this.username = this.cookies.get('username');
      this.login();
    }
  },
  data() {
    return {
      showProfile: false,
      username: "",
      isLoggedIn: false
    }
  },
  methods: {
    saveUsername: function() {
      this.cookies.set("username", this.username, "365d");
      this.showProfile = false;
      this.login();
    },
    login: function() {
      socket.emit("User Login", {"username": this.username}, function(user) {
        state.user = user;
      });
      this.isLoggedIn= true;
    }
  }
}
</script>

<style>
</style>
