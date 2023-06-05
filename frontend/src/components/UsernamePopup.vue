<template>
  <div @click="show = true" class="d-flex">
    <span id="username-display">{{ username }}</span>
    <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" fill="currentColor" class="bi bi-pen mt-1" viewBox="0 0 16 16" data-darkreader-inline-fill="" style="--darkreader-inline-fill:currentColor;">
      <path d="m13.498.795.149-.149a1.207 1.207 0 1 1 1.707 1.708l-.149.148a1.5 1.5 0 0 1-.059 2.059L4.854 14.854a.5.5 0 0 1-.233.131l-4 1a.5.5 0 0 1-.606-.606l1-4a.5.5 0 0 1 .131-.232l9.642-9.642a.5.5 0 0 0-.642.056L6.854 4.854a.5.5 0 1 1-.708-.708L9.44.854A1.5 1.5 0 0 1 11.5.796a1.5 1.5 0 0 1 1.998-.001zm-.644.766a.5.5 0 0 0-.707 0L1.95 11.756l-.764 3.057 3.057-.764L14.44 3.854a.5.5 0 0 0 0-.708l-1.585-1.585z"></path>
    </svg>
  </div>
  <Popup  v-if="show" title="Kérlek írd be hogyan hívnak:" @cancel="show = false" @confirm="this.saveUsername()">
    <p>Hello</p>
    <input type="text" v-model.trim="username">
    <br>
  </Popup>
</template>

<script>
import Popup from './Popup.vue';
import { useCookies } from "vue3-cookies";

export default {
  name: 'UsernamePopup',
  components: {
    Popup
  },
  setup() {
    const { cookies } = useCookies();
    return { cookies };
  },
  emits: ['cancel'],
  mounted() {
    this.username = this.cookies.get('username');
    if (!this.$cookies.isKey('username')) {
      this.show = true;
    }
    console.log("Mounted with:" + this.username);
  },
  data() {
    return {
      show: false,
      username: ""
    }
  },
  methods: {
    saveUsername: function() {
      this.cookies.set("username", this.username, "365d");
      this.show = false;
    }
  }
}
</script>

<style>
</style>
