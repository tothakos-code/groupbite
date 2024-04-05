<template>
  <div class="row ms-2">
    <div class="">
      <h1 class="">
        Plugin Config {{ $route.params.id }}
      </h1>
    </div>
    <div class="">
      <div
        v-for="(setting, id) in settings"
        :key="id"
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
    name: 'PluginConfiguration',
    setup() {
      const auth = useAuth();
      return {
        auth
      }
    },
    data() {
      return {
        settings: {}
      }
    },
    mounted() {
      this.getSettings()
    },
    methods: {
      getSettings: function () {
        axios.get(`http://${window.location.host}/api/vendor/${this.$route.params.id}/settings/get`)
          .then(response => {
            this.settings = response.data
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
