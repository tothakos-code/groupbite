<template>
  <Popup
    :show-modal="show"
    title="Profil beállítások"
    @cancel="onCancel()"
    @confirm="updateUser()"
  >
    <p>A nevednek a könnyebb beazonosítás miatt egyedinek kell lennie. Használj egy becenevet amiről mindneki tudja, hogy te vagy az.</p>
    <p>A nevedet itt tudod megváltoztatni:</p>
    <div class="input-group mb-3">
      <span class="input-group-text">Név</span>
      <input
        v-model.trim="username"
        type="text"
        class="form-control"
        placeholder="Username"
        aria-label="Username"
        aria-describedby="basic-addon1"
      >
    </div>
    <!-- <p>A szabadság táblázatban így szerepel a neved:</p>
    <div class="input-group mb-3">
      <span class="input-group-text">Szabadság tábla név:</span>
      <input type="text" v-model.trim="vt_name" class="form-control" placeholder="Username" aria-label="Username" aria-describedby="basic-addon1">
    </div> -->
    <span class="input-group-radio">Felület szine:</span>
    <div class="d-flex justify-content-around m-2">
      <input
        id="falusi-outlined"
        v-model="ui_color"
        type="radio"
        class="btn-check"
        name="options-outlined"
        value="falusi"
        autocomplete="off"
        @change="onColorChange()"
      >
      <label
        class="btn btn-outline-falusi"
        for="falusi-outlined"
      >Alap</label>

      <input
        id="info-outlined"
        v-model="ui_color"
        type="radio"
        class="btn-check"
        name="options-outlined"
        value="steelblue"
        autocomplete="off"
        @change="onColorChange()"
      >
      <label
        class="btn btn-outline-steelblue"
        for="info-outlined"
      >Acélkék</label>

      <input
        id="danger-outlined"
        v-model="ui_color"
        type="radio"
        class="btn-check"
        name="options-outlined"
        value="raspberry"
        autocomplete="off"
        @change="onColorChange()"
      >
      <label
        class="btn btn-outline-raspberry"
        for="danger-outlined"
      >Málna</label>

      <input
        id="warning1-outlined"
        v-model="ui_color"
        type="radio"
        class="btn-check"
        name="options-outlined"
        value="tigragold"
        autocomplete="off"
        @change="onColorChange()"
      >
      <label
        class="btn btn-outline-tigragold"
        for="warning1-outlined"
      >Tigra</label>
    </div>
  </Popup>
</template>

<script>
import Popup from './Popup.vue';
import { useCookies } from "vue3-cookies";
import { state, socket } from "@/socket";
import { notify } from "@kyvg/vue3-notification";

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
      theme: "",
      ui_color: ""
    }
  },
  computed: {
    loggedInUsername() {
      return this.auth.user.username;
    }
  },
  mounted() {
    this.username = this.loggedInUsername;
    this.ui_color = this.auth.user.ui_color;
  },
  methods: {
    updateUser: function() {
      let user_update_obj = {};
      user_update_obj.id = this.auth.user.id
      if (this.username !== this.auth.user.username) {
        user_update_obj.username = this.username
      }
      // if (this.vt_name !== this.auth.user.vt_name) {
      //   user_update_obj.vt_name = this.vt_name
      // }
      user_update_obj.ui_color = this.ui_color

      socket.emit("User Update", user_update_obj, (user) => {
        if (user.error === undefined) {
          this.cookies.set("username", user.username, "365d");
          this.auth.user = user;
          this.$emit('cancel');
        } else {
          notify({
            type: "warn",
            text: user.error,
          });
        }
      });
    },
    onCancel: function() {
      fetch(`http://${window.location.host}/api/user/get/${this.auth.user.id}`,{
        method: "get",
        headers: {
          "Content-Type": "application/json",
        }
      })
        .then(response => response.json())
          .then(data => {
            this.auth.user.ui_color = data.ui_color;
            this.ui_color = data.ui_color;
          })
          .catch(error => console.error(error))
      this.$emit('cancel')
    },
    onColorChange: function() {
      this.auth.user.ui_color = this.ui_color
    }
  }
}
</script>

<style>

</style>
