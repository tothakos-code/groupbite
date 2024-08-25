<template>
  <div class="row ms-2">
    <div class="">
      <div
        v-for="(setting, sid) in vendor.settings"
        :key="sid"
        class="my-2 w-25"
      >
        <label :for="setting.id">
          {{ setting.name }}:
        </label>
        <input
          v-model="setting.value"
          :type="setting.type == 'BOOL' ? 'checkbox' : setting.type == 'INT' ? 'number' : setting.type == 'STRBOX' ? 'textarea' : 'text'"
          class="form-control"
          :class="{'form-check-input': setting.type == 'BOOL' }"
          :name="setting.id"
        >
      </div>
      <button
        class="btn mt-1"
        :class="['btn-' + auth.getUserColor ]"
        type="button"
        name="save"
        @click="saveSettings()"
      >
        Mentés
      </button>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { useAuth } from "@/stores/auth";
import { notify } from "@kyvg/vue3-notification";

export default {
    name: "VendorSettings",
    setup() {
      const auth = useAuth();
      return {
        auth
      }
    },
    data() {
      return {
        vendor: {}
      }
    },
    mounted() {
      this.getSettings()
    },
    methods: {
      getSettings: function () {
        axios.get(`http://${window.location.host}/api/vendor/${this.$route.params.id}/get`)
          .then(response => {
            this.vendor = response.data
          })
          .catch(e => {
              console.log(e);
          })
      },
      saveSettings: function () {
        axios.post(
          `http://${window.location.host}/api/vendor/${this.$route.params.id}/settings/save`,
          {
            "data": this.vendor.settings,
          }
        )
          .then(response => {
            this.settings = response.data
            notify({
              type: "info",
              text: "Vendor beállítások mentése sikeres!",
            });
          })
          .catch(e => {
              console.log(e);
              notify({
                type: "error",
                text: "Vendor beállítások mentése nem sikerült!",
              });
          })
      },
    }
};
</script>

<style scoped>
</style>
