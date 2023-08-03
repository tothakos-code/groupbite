<template>
  <Popup  :showModal="show" title="Profil beállítások" @cancel="$emit('cancel')" @confirm="this.updateUser()">
    <p>A nevednek a könnyebb beazonosítás miatt egyedinek kell lennie. Használj egy becenevet amiről mindneki tudja, hogy te vagy az.</p>
    <p>A nevedet itt tudod megváltoztatni:</p>
    <div class="input-group mb-3">
      <span class="input-group-text">Név</span>
      <input type="text" v-model.trim="username" class="form-control" placeholder="Username" aria-label="Username" aria-describedby="basic-addon1">
    </div>
    <p>A szabadság táblázatban így szerepel a neved:</p>
    <div class="input-group mb-3">
      <span class="input-group-text">Szabadság tábla név:</span>
      <input type="text" v-model.trim="vt_name" class="form-control" placeholder="Username" aria-label="Username" aria-describedby="basic-addon1">
    </div>
    <div class="input-group mb-3">
      <span class="input-group-radio">Téma:</span>
      <input type="radio" class="form-control">
    </div>
  </Popup>
</template>

<script>
import Popup from './Popup.vue';
import { useCookies } from "vue3-cookies";
import { state, socket } from "@/socket";

export default {
  name: 'UserProfilePopup',
  components: {
    Popup
  },
  props: {
    show: Boolean
  },
  emits: ['cancel', 'confirm'],
  setup() {
    const { cookies } = useCookies();
    return { cookies };
  },
  data() {
    return {
      username: "",
      vt_name: "",
      theme: ""
    }
  },
  mounted() {
    this.username = this.loggedInUsername;
  },
  methods: {
    updateUser: function() {
      socket.emit("User Update", {"id": state.user.id ,"username": this.username, "vt-name": this.vt_name}, (user) => {
        if (user.error === undefined) {
          this.cookies.set("username", user.username, "365d");
          state.user = user;
          this.$emit('cancel');
        } else {
          alert("Helytelen felhasználónév!")
        }
      });
    }
  },
  computed: {
    loggedInUsername() {
      return state.user.username;
    }
  }
}
</script>

<style>
</style>
