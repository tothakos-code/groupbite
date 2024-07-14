<template>
  <div class="">
    <div
      v-if="menus.length == 0"
      class="mt-2"
    >
      <span class="h4">
        Hozz létre egy menüt, hogy feltudd tölteni
      </span>
    </div>
    <div
      v-else
      class=""
    >
      <div class="row ms-2">
        <div
          class="row my-2"
        >
          <div class="col-auto">
            <label for="itemName">
              Válassz egy Menüt:
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
          <div
            v-if="selectedMenu"
            class="row mt-2"
          >
            <span class="row ms-1 h4">
              Új étel hozzáadása:
            </span>
            <div class="col-2">
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

            <div class="col-2">
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
            <div class="col-2">
              <label for="itemCategory">
                Kategória:
              </label>
              <input
                v-model="newItem.category"
                type="text"
                name="itemCategory"
                class="form-control"
              >
            </div>
            <div class="col-1">
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
            <div class="col-1">
              <label
                for="itemQuantity"
                title="Végtelen mennyiséghez adj megy egy negatív számot"
              >
                Mennyiség:
              </label>
              <input
                v-model="newItem.quantity"
                type="number"
                name="itemQuantity"
                class="form-control"
              >
            </div>
            <button
              class="btn col-auto"
              :class="['btn-' + auth.getUserColor ]"
              type="button"
              name="save"
              @click="addToMenu()"
            >
              Menühöz adás
            </button>
          </div>
        </div>
      </div>
      <div class="mt-2">
        <table class="table table-striped table-bordered table-hover">
          <thead>
            <tr>
              <th
                scope="col"
                class="col-auto"
              >
                #
              </th>
              <th
                scope="col"
                class="col-auto"
              >
                Név
              </th>
              <th
                scope="col"
                class="col-auto"
              >
                Kategória
              </th>
              <th
                scope="col"
                class="col-auto"
              >
                Sorrend index
              </th>
              <th
                scope="col"
                class="col-auto"
              >
                Műveletek
              </th>
            </tr>
          </thead>
          <tbody class="table-group-divider">
            <template
              v-for="[id, menuItem] in items"
              :key="id"
            >
              <tr>
                <td
                  scope="row"
                  class="col-auto"
                >
                  {{ menuItem.id }}
                </td>
                <td>
                  <input
                    v-if="menuItem.isEditing"
                    v-model="menuItem.name"
                    class="form-control"
                    type="text"
                  >
                  <span v-else>
                    {{ menuItem.name }}
                  </span>
                </td>
                <td>
                  <input
                    v-if="menuItem.isEditing"
                    v-model="menuItem.category"
                    class="form-control"

                    type="text"
                  >
                  <span v-else>
                    {{ menuItem.category }}
                  </span>
                </td>
                <td>
                  <input
                    v-if="menuItem.isEditing"
                    v-model="menuItem.index"
                    class="form-control"
                    type="number"
                  >
                  <span v-else>
                    {{ menuItem.index }}
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
                    @click="newSize(menuItem.id)"
                  >
                    Új méret
                  </button>
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
              <tr>
                <td />
                <td colSpan="4">
                  <table class="table mb-0 table-striped table-hover">
                    <thead>
                      <tr>
                        <th
                          scope="col"
                          class="col-auto"
                        >
                          Méret
                        </th>
                        <th
                          scope="col"
                          class="col-auto"
                        >
                          Ár
                        </th>
                        <th
                          scope="col"
                          class="col-auto"
                        >
                          Mennyiség
                        </th>
                        <th
                          scope="col"
                          class="col-auto"
                        >
                          Sorrend index
                        </th>
                        <th
                          scope="col"
                          class="col-auto"
                        >
                          Műveletek
                        </th>
                      </tr>
                      <tr
                        v-for="[sizeId, size] in menuItem.sizes"
                        :key="'size-' + sizeId"
                      >
                        <td>
                          <input
                            v-if="size.isEditing"
                            v-model="size.name"
                            class="form-control"

                            type="text"
                          >
                          <span v-else>
                            {{ size.name }}
                          </span>
                        </td>
                        <td>
                          <input
                            v-if="size.isEditing"
                            v-model="size.price"
                            class="form-control"
                            type="number"
                          >
                          <span v-else>
                            {{ size.price }}
                          </span>
                        </td>
                        <td>
                          <input
                            v-if="size.isEditing"
                            v-model="size.quantity"
                            class="form-control"
                            type="number"
                          >
                          <span v-else>
                            {{ size.quantity }}
                          </span>
                        </td>
                        <td>
                          <input
                            v-if="size.isEditing"
                            v-model="size.index"
                            class="form-control"
                            type="number"
                          >
                          <span v-else>
                            {{ size.index }}
                          </span>
                        </td>
                        <td>
                          <button
                            v-if="!size.isEditing"
                            type="button"
                            name="button"
                            class="btn"
                            title="Szerkesztés"
                            :class="['btn-outline-' + auth.getUserColor ]"
                            @click="editSize(menuItem.id, size.id)"
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
                              @click="updateSize(menuItem.id, size.id)"
                            >
                              Mentés
                            </button>
                            <button
                              type="button"
                              name="button"
                              class="btn"
                              title="Mégse"
                              :class="['btn-outline-' + auth.getUserColor ]"
                              @click="cancelSizeEdit(menuItem.id, size.id)"
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
                            @click="deleteSize(menuItem.id, size.id)"
                          >
                            Törlés
                          </button>
                        </td>
                      </tr>
                    </thead>
                  </table>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>
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
          category: "",
          price: 0,
          quantity: -1,
          index: 0,
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
        axios.get(`http://${window.location.host}/api/menu/${this.$route.params.id}/menu-get`)
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

            let menuItemsMap = new Map();
            response.data.forEach(item => {
              item.isEditing = false


              let sizesMap = new Map();
              item.sizes.forEach(size => {
                size.isEditing = false;
                sizesMap.set(size.id, size);
              });
              item.sizes = sizesMap;
              menuItemsMap.set(item.id, item)
            });

            this.items = menuItemsMap;
            console.log(this.items);
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
      newSize: function (itemId) {
        let newSize = {
            "id": -1,
            "name": "",
            "price": 0,
            "quantity": -1,
            "index": 0,
            "isEditing": true
        }

        this.items.get(itemId).sizes.set(-1, newSize)
      },
      edit: function (menu_id) {
        const item = this.items.get(menu_id)
        this.items.set(item.id, { ...item, isEditing: true})
      },
      editSize: function (itemId, sizeId) {
        const size = this.items.get(itemId).sizes.get(sizeId)
        this.items.get(itemId).sizes.set(size.id, { ...size, isEditing: true})
      },
      cancelEdit: function (itemId) {
        const item = this.items.get(itemId)
        this.items.set(item.id, { ...item, isEditing: false})
      },
      cancelSizeEdit: function (itemId, sizeId) {
        const size = this.items.get(itemId).sizes.get(sizeId)
        this.items.get(itemId).sizes.set(size.id, { ...size, isEditing: false})
      },
      updateItem: function (item_id) {
        const item = this.items.get(item_id)
        this.items.set(item.id, { ...item, isEditing: false})
        axios.post(`http://${window.location.host}/api/menu/${this.$route.params.id}/item-update`, {'data': item})
          .then(() => {
            this.getItemList()
            notify({
              type: "info",
              text: "Étel frissítés sikeres!",
            });
          })
          .catch(e => {
              console.log(e);
              notify({
                type: "error",
                text: "Étel frissítés nem sikerült!",
              });
          })
      },
      updateSize: function (itemId, sizeId) {
        const size = this.items.get(itemId).sizes.get(sizeId)
        this.items.get(itemId).sizes.set(size.id, { ...size, isEditing: false})
        axios.post(`http://${window.location.host}/api/menu/${this.$route.params.id}/item-size-update`, {'data': size, 'item': itemId})
          .then(() => {
            this.getItemList()
            notify({
              type: "info",
              text: "Méret frissítés sikeres!",
            });
          })
          .catch(e => {
              console.log(e);
              notify({
                type: "error",
                text: "Méret frissítés nem sikerült!",
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
              text: "Étel törlés sikeres!",
            });
          })
          .catch(e => {
              console.log(e);
              notify({
                type: "error",
                text: "Étel törlés nem sikerült!",
              });
          })
      },
      deleteSize: function (itemId, sizeId) {
        const size = this.items.get(itemId).sizes.get(sizeId)
        this.items.get(itemId).sizes.set(size.id, { ...size, isEditing: false})
        axios.post(`http://${window.location.host}/api/menu/${this.$route.params.id}/item-size-delete`, {'data': size})
          .then(() => {
            this.getItemList()
            notify({
              type: "info",
              text: "Méret törlés sikeres!",
            });
          })
          .catch(e => {
              console.log(e);
              notify({
                type: "error",
                text: "Méret törlés nem sikerült!",
              });
          })
      },
    }
};
</script>

<style scoped>
</style>
