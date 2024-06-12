<template>
  <div class="row ms-2">
    <div class="">
      <div
        class="row my-2 w-75"
      >
        <div class="col-auto">
          <label for="itemName">
            Menü:
          </label>
          <select
            v-model="selectedMenu"
            name="itemMenu"
            class="form-control"
          >
            <option
              v-for="m in menus"
              :key="m.id"
              :value="m.id"
            >
              {{ m.name }} - {{ m.date }}
            </option>
          </select>
        </div>
        <div class="col-auto">
          <label for="itemName">
            Név:
          </label>
          <input
            v-model="item.name"
            type="text"
            name="itemName"
            class="form-control"
          >
        </div>

        <div class="col-auto">
          <label for="itemSize">
            Méret:
          </label>
          <input
            v-model="item.size"
            type="text"
            name="itemSize"
            class="form-control"
          >
        </div>
        <div class="col-auto">
          <label for="itemPrice">
            Ár:
          </label>
          <input
            v-model="item.price"
            type="number"
            name="itemPrice"
            class="form-control"
          >
        </div>
      </div>
      <button
        class="btn"
        :class="['btn-' + auth.getUserColor ]"
        type="button"
        name="save"
        @click="addToMenu()"
      >
        Menühöz adás
      </button>
    </div>
  </div>
  <div class="">
    <table class="table table-striped table-hover">
      <thead>
        <tr>
          <th scope="col">
            #
          </th>
          <th scope="col">
            Név
          </th>
          <th scope="col">
            Dátum
          </th>
          <th scope="col">
            Gyakoriság
          </th>
        </tr>
      </thead>
      <tbody class="table-group-divider">
        <tr
          v-for="menuItem, index in items"
          :key="index"
        >
          <th scope="row">
            {{ menuItem.id }}
          </th>
          <td>
            {{ menuItem.name }}
          </td>
          <td>
            {{ menuItem.size }}
          </td>
          <td>
            {{ menuItem.price }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from 'axios';
import { useAuth } from '@/stores/auth';
import { notify } from "@kyvg/vue3-notification";

export default {
    name: 'VendorItemManager',
    setup() {
      const auth = useAuth();
      return {
        auth
      }
    },
    data() {
      return {
        menus: [],
        selectedMenu: "",
        item: {
          name: "",
          size: "",
          price: 0,
        },
        items: []
      }
    },
    watch: {
      selectedMenu() {
        this.getItemList()
      }
    },
    mounted() {
      this.getMenuList()
    },
    methods: {
      getMenuList: function () {
        axios.get(`http://${window.location.host}/api/menu/${this.$route.params.id}/get`)
          .then(response => {
            this.menus = response.data
          })
          .catch(e => {
              console.log(e);
          })
      },
      getItemList: function () {
        axios.get(`http://${window.location.host}/api/menu/${this.$route.params.id}/get-items/${this.selectedMenu}`)
          .then(response => {
            console.log(response);
            this.items = response.data
          })
          .catch(e => {
              console.log(e);
          })
      },
      addToMenu: function () {
        axios.post(`http://${window.location.host}/api/menu/${this.$route.params.id}/item-add`, {'data':this.item, 'menu': this.selectedMenu})
          .then(() => {
            this.getMenuList()
            notify({
              type: "info",
              text: "MenuItem hozzáadása sikeres!",
            });
          })
          .catch(e => {
              console.log(e);
              notify({
                type: "error",
                text: "MenuItem hozzáadása nem sikerült!",
              });
          })
      },
    }
};
</script>

<style scoped>
</style>
