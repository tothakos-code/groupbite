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
      <v-btn
        class="btn mt-2 bg-primary"
        type="button"
        name="save"
        @click="createVendor()"
      >
        Mentés
      </v-btn>
    </div>
  </div>
</template>

<script>
import { useAuth } from "@/stores/auth";
import { useVendorStore } from "@/stores/vendor";

export default {
    name: "VendorAdd",
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
        vendor: {
          "name":"",
          "settings":{
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
            "closure_scheduler": {
              "name": "Rendelés automatikus zárás figyelmeztetés (formátum: hh:mm)",
              "type": "STR",
              "value": "manual",
              "section": "root"
            },
            "closed_scheduler": {
              "name": "Rendelés automatikus lezárása (formátum: hh:mm)",
              "type": "STR",
              "value": "manual",
              "section": "root"
            },
            "order_text_template": {
              "name": "Rendelés szöveg sor minta",
              "type": "STR",
              "value": "${quantity}x ${item_name} ${size_name}\\n",
              "section": "root"
            },
          }
        }
      }
    },
    mounted() {
    },
    methods: {
      createVendor: function () {
        this.vendorStore.add(this.vendor)
          .then(() => {

            this.$router.push("/admin")
          })
      },
    }
};
</script>

<style scoped>
</style>
