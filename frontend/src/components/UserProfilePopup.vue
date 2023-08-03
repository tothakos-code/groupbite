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
    <span class="input-group-radio">Téma:</span>
    <div class="d-flex justify-content-around">
      <input type="radio" class="btn-check" name="options-outlined" id="warning-outlined" autocomplete="off" checked>
      <label class="btn btn-outline-warning" for="warning-outlined">Alap</label>

      <input type="radio" class="btn-check" name="options-outlined" id="info-outlined" autocomplete="off">
      <label class="btn btn-outline-info" for="info-outlined">Óceán</label>

      <input type="radio" class="btn-check" name="options-outlined" id="danger-outlined" autocomplete="off">
      <label class="btn btn-outline-danger" for="danger-outlined">Málna</label>

      <input type="radio" class="btn-check" name="options-outlined" id="warning1-outlined" autocomplete="off">
      <label class="btn btn-outline-warning" for="warning1-outlined">Tigra</label>
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
