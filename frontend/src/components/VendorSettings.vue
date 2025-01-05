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
      <v-btn
        class="bg-primary mt-1"
        type="button"
        name="save"
        @click="saveSettings()"
      >
        Mentés
      </v-btn>
    </div>
  </div>
</template>

<script>
import { useVendorStore } from "@/stores/vendor";
import { useAuth } from "@/stores/auth";

export default {
    name: "VendorSettings",
    setup() {
      const auth = useAuth();
      const vendorStore = useVendorStore();

      return {
        auth,
        vendorStore
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
        this.vendorStore.fetchVendor(this.$route.params.id)
          .then(response => {
            this.vendor = response.data.data

          })
      },
      saveSettings: function () {
        this.vendorStore.saveSettings(this.$route.params.id, this.vendor.settings)
          .then(response => {
            this.settings = response.data
          })
      },
    }
};
</script>

<style scoped>
</style>
