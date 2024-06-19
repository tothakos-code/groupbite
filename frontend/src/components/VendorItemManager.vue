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
            v-model="newItem.name"
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
            v-model="newItem.size"
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
            v-model="newItem.price"
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
          <th scope="col">
            Műveletek
          </th>
        </tr>
      </thead>
      <tbody class="table-group-divider">
        <tr
          v-for="[index, menuItem] in items"
          :key="index"
        >
          <th scope="row">
            {{ menuItem.id }}
          </th>
          <td>
            <input
              v-if="menuItem.isEditing"
              v-model="menuItem.name"
              type="text"
            >
            <span v-else>
              {{ menuItem.name }}
            </span>
          </td>
          <td>
            <input
              v-if="menuItem.isEditing"
              v-model="menuItem.size"
              type="text"
            >
            <span v-else>
              {{ menuItem.size }}
            </span>
          </td>
          <td>
            <input
              v-if="menuItem.isEditing"
              v-model="menuItem.price"
              type="number"
            >
            <span v-else>
              {{ menuItem.price }}
            </span>
          </td>
          <td>
            <button
              v-if="!menuItem.isEditing"
              type="button"
              name="button"
              class="btn"
              title="Szerkesztés"
              :class="['btn-outline-' + auth.getUserColor ]"
              @click="edit(menuItem.id)"
            >
              Szerkesztés
            </button>
            <div v-else>
              <button
                type="button"
                name="button"
                class="btn"
                title="Mentés"
                :class="['btn-outline-' + auth.getUserColor ]"
                @click="updateItem(menuItem.id)"
              >
                Mentés
              </button>
              <button
                type="button"
                name="button"
                class="btn"
                title="Mégse"
                :class="['btn-outline-' + auth.getUserColor ]"
                @click="cancelEdit(menuItem.id)"
              >
                Mégse
              </button>
            </div>
            <button
              type="button"
              name="button"
              class="btn"
              title="Törlés"
              :class="['btn-outline-' + auth.getUserColor ]"
              @click="deleteItem(menuItem.id)"
            >
              Törlés
            </button>
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
        newItem: {
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
            let newItemsList = new Map(
              response.data.map(
                item => [item.id, item]
              )
            )
            this.items.forEach((item) => {
              item.isEditing = false
            });
            this.items = newItemsList;
          })
          .catch(e => {
              console.log(e);
          })
      },
      addToMenu: function () {
        axios.post(`http://${window.location.host}/api/menu/${this.$route.params.id}/item-add`, {'data':this.newItem, 'menu': this.selectedMenu})
          .then(() => {
            this.getItemList()
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
      edit: function (menu_id) {
        const item = this.items.get(menu_id)
        this.items.set(item.id, { ...item, isEditing: true})
      },
      cancelEdit: function (menu_id) {
        const item = this.items.get(menu_id)
        this.items.set(item.id, { ...item, isEditing: false})
      },
      updateItem: function (item_id) {
        const item = this.items.get(item_id)
        this.items.set(item.id, { ...item, isEditing: false})
        axios.post(`http://${window.location.host}/api/menu/${this.$route.params.id}/item-update`, {'data': item})
          .then(() => {
            this.getItemList()
            notify({
              type: "info",
              text: "Item frissítés sikeres!",
            });
          })
          .catch(e => {
              console.log(e);
              notify({
                type: "error",
                text: "Item frissítés nem sikerült!",
              });
          })
      },
      deleteItem: function (item_id) {
        const item = this.items.get(item_id)
        this.items.set(item.id, { ...item, isEditing: false})
        axios.post(`http://${window.location.host}/api/menu/${this.$route.params.id}/item-delete`, {'data': item})
          .then(() => {
            this.getItemList()
            notify({
              type: "info",
              text: "Item törlés sikeres!",
            });
          })
          .catch(e => {
              console.log(e);
              notify({
                type: "error",
                text: "Item törlés nem sikerült!",
              });
          })
      },
    }
};
</script>

<style scoped>
</style>
