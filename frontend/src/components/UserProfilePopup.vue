<template>
  <Popup
    :show-modal="show"
    title="Profil beállítások"
    confirm-text="Mentés"
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
    <!--
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
    </div> -->
  </Popup>
</template>

<script>
import Popup from "./Popup.vue";
import { useAuth } from "@/stores/auth";

export default {
  name: "UserProfilePopup",
  components: {
    Popup
  },
  props: {
    show: Boolean
  },
  emits: ["cancel", "confirm"],
  setup() {
    const auth = useAuth();
    return { auth };
  },
  data() {
    return {
      username: this.auth.user.username,
      theme: "",
      ui_color: ""
    }
  },

  methods: {
    updateUser: function() {
      let user_update_obj = {};
      user_update_obj.id = this.auth.user.id
      if (this.username !== this.auth.user.username) {
        user_update_obj.username = this.username
      }

      user_update_obj.ui_color = this.ui_color
      this.auth.update(user_update_obj)
        .then(response => {
        let user = response.data.data;
        if (response.data.error === undefined) {
          this.auth.$patch({
            user: user
          });
          this.$emit("cancel");
        }
      });
    },
    onCancel: function() {
      this.$emit("cancel")
    },
    onColorChange: function() {
      this.auth.user.ui_color = this.ui_color
    }
  }
}
</script>

<style>

</style>
