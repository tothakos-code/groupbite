<template>
  <div class="row ms-2">
    <div class="">
      <h1 class="">
        Vendor settings {{ vendor.name }}
      </h1>
    </div>
    <div class="">
      <div
        v-for="(setting, sid) in vendor.settings"
        :key="sid"
        class=""
      >
        <label :for="setting.id">{{ setting.name }}
          <input
            v-model="setting.value"
            type="text"
            :name="setting.id"
          >
        </label>
      </div>
      <button
        class="btn"
        :class="['btn-' + auth.userColor.value ]"
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
import axios from 'axios';
import { useAuth } from '@/auth';

export default {
    name: 'PluginSettings',
    props: {
      id:{
        type: String,
        required: true
      },
    },
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
        axios.post(`http://${window.location.host}/api/vendor/${this.$route.params.id}/settings/save`, {'data':this.settings})
          .then(response => {
            this.settings = response.data
          })
          .catch(e => {
              console.log(e);
          })
      },
    }
};
</script>

<style scoped>
</style>
