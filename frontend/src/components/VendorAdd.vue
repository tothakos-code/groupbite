<template>
  <div class="row ms-2">
    <div class="">
      <h1 class="">
        Új üzlet létrehozás
      </h1>
    </div>
    <div class="">
      <div
        class=""
      >
        <label for="short-name">Rövid Név:
        </label>
        <input
          v-model="vendor.name"
          class="form-control"
          type="text"
          name="short-name"
          required
        >

        <label for="full-name">Teljes név:
        </label>
        <input
          v-model="vendor.settings.title.value"
          type="text"
          name="full-name"
          class="form-control"
          required
        >

        <label for="transport_price">Szállítási Díj:
        </label>
        <input
          v-model="vendor.settings.transport_price.value"
          type="number"
          name="transport_price"
          class="form-control"
        >

        <label for="transport_price">Rendelés megjegyzés példa:
        </label>
        <input
          v-model="vendor.settings.comment_example.value"
          type="text"
          name="transport_price"
          class="form-control"
        >
      </div>
      <button
        class="btn mt-2"
        :class="['btn-' + auth.getUserColor ]"
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
import { useAuth } from '@/stores/auth';
import { notify } from "@kyvg/vue3-notification";

export default {
    name: 'VendorAdd',
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
            "link": {
              "name": "Eredeti oldal elérhetősége",
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
            "comment_example": {
              "name": "Rendelés megjegyzés példa",
              "type": "STR",
              "value": "Bárdi autó épületén jobb oldalt fotocellás ajtó, balra lift, 3. em, jobbra csengő Tigra Kft.",
              "section": "root"
            },
            "order_text_template": {
              "name": "Rendelés szöveg sor minta",
              "type": "STR",
              "value": "${quantity}x ${item_name} ${size_name}\\n",
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
            notify({
              type: "info",
              text: "Üzlet hozzáadása sikeres!",
            });
            this.$router.push("/admin")
          })
          .catch(e => {
              console.log(e);
              notify({
                type: "error",
                text: "Üzlet hozzáadása nem sikerült!",
              });
          })
      },
    }
};
</script>

<style scoped>
</style>
