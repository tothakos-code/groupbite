<template>
  <Popup  :showModal="show" title="Név választás" @cancel="$emit('cancel')" @confirm="this.saveUsername()">
    <p>Egy név ami alapján beazonosíthatnak téged.</p>
    <p>Nincs külön regisztráció. A név megadásával már létre is jön a fiókod.</p>
    <p>A fiókodba belépni későb a neved megadásával tudsz.</p>
    <div class="input-group mb-3">
      <span class="input-group-text">Név</span>
      <input type="text" v-model.trim="username" class="form-control" placeholder="Username" aria-label="Username" aria-describedby="basic-addon1">
    </div>
  </Popup>
</template>

<script>
import Popup from './Popup.vue';
import { useCookies } from "vue3-cookies";
import { useAuth } from "@/auth.js";

export default {
  name: 'UserLoginPopup',
  components: {
    Popup
  },
  props: {
    show: Boolean
  },
  emits: ['cancel', 'confirm'],
  setup() {
    const { cookies } = useCookies();
    const auth = useAuth();
    return {
      cookies,
      auth
    }
  },
  data() {
    return {
      username: ""
    }
  },
  mounted() {
    if (this.$cookies.isKey('username')) {
      this.username = this.cookies.get('username');
      this.auth.login(this.username)
    }

  },
  methods: {
    saveUsername: function() {
      this.cookies.set("username", this.username, "365d");
      this.login();
    },
    login: function() {
      this.auth.login(this.username)
      this.$emit('cancel')

    }
  }
}
</script>

<style>
</style>
