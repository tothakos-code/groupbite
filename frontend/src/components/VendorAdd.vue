<template>
  <div class="row ms-2">
    <div class="">
      <h1 class="">
        Vendor létrehozás
      </h1>
    </div>
    <div class="">
      <div
        class=""
      >
        <label for="short-name">rövid Név:
          <input
            v-model="vendor.name"
            type="text"
            name="short-name"
            required
          >
        </label>

        <label for="full-name">Teljes név:
          <input
            v-model="vendor.settings.title.value"
            type="text"
            name="full-name"
            required
          >
        </label>

        <label for="transport_price">Szállítási Díj:
          <input
            v-model="vendor.settings.transport_price.value"
            type="number"
            name="transport_price"
          >
        </label>
      </div>
      <button
        class="btn"
        :class="['btn-' + auth.userColor.value ]"
        type="button"
        name="save"
        @click="createVendor()"
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
        vendor: {
          'name':"",
          'settings':{
            "title": {
              "name": "Cím",
              "type": "STR",
              "value": "",
              "section": "root"
            },
            "transport_price": {
              "name": "Szállítási díj",
              "type": "INT",
              "value": "0",
              "section": "root"
            },
          },
          'configuration':{},
        }
      }
    },
    mounted() {
    },
    methods: {
      createVendor: function () {
        axios.post(`http://${window.location.host}/api/vendor/create`, {'data':this.vendor})
          .then(response => {
            console.log(response.data);
            // this.settings = response.data
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
