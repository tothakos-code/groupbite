<template>
  <Popup  :showModal="show" title="Profil beállítások" @cancel="this.onCancel()" @confirm="this.updateUser()">
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
      <input type="radio" class="btn-check" name="options-outlined" id="falusi-outlined" value="falusi" autocomplete="off" @change="this.onColorChange()" v-model="ui_color">
      <label class="btn btn-outline-falusi" for="falusi-outlined">Alap</label>

      <input type="radio" class="btn-check" name="options-outlined" id="info-outlined" value="steelblue" autocomplete="off" @change="this.onColorChange()" v-model="ui_color">
      <label class="btn btn-outline-steelblue" for="info-outlined">Acélkék</label>

      <input type="radio" class="btn-check" name="options-outlined" id="danger-outlined" value="raspberry" autocomplete="off" @change="this.onColorChange()" v-model="ui_color">
      <label class="btn btn-outline-raspberry" for="danger-outlined">Málna</label>

      <input type="radio" class="btn-check" name="options-outlined" id="warning1-outlined" value="tigragold" autocomplete="off" @change="this.onColorChange()" v-model="ui_color">
      <label class="btn btn-outline-tigragold" for="warning1-outlined">Tigra</label>
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
      theme: "",
      ui_color: ""
    }
  },
  mounted() {
    this.username = this.loggedInUsername;
  },
  methods: {
    updateUser: function() {
      let user_update_obj = {};
      user_update_obj.id = state.user.id
      if (this.username !== state.user.username) {
        user_update_obj.username = this.username
      }
      // if (this.vt_name !== state.user.vt_name) {
      //   user_update_obj.vt_name = this.vt_name
      // }
      user_update_obj.ui_color = this.ui_color

      socket.emit("User Update", user_update_obj, (user) => {
        if (user.error === undefined) {
          this.cookies.set("username", user.username, "365d");
          state.user = user;
          this.$emit('cancel');
        } else {
          alert("Helytelen felhasználónév!")
        }
      });
    },
    onCancel: function() {
      fetch(`http://${window.location.hostname}/api/user/get/${state.user.id}`,{
        method: "get",
        headers: {
          "Content-Type": "application/json",
        }
      })
        .then(response => response.json())
          .then(data => {
            state.user.ui_color = data.ui_color;
            this.ui_color = data.ui_color;
          })
          .catch(error => console.error(error))
      this.$emit('cancel')
    },
    onColorChange: function() {
      state.user.ui_color = this.ui_color
    }
  },
  computed: {
    loggedInUsername() {
      return state.user.username;
    },
    usercolor(){
      return state.user.ui_color ? state.user.ui_color : "falusi";
    }
  }
}
</script>

<style>

</style>
