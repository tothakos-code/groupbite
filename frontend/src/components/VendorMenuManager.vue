<template>
  <div class="row ms-2">
    <div class="">
      <div
        class="row my-2"
      >
        <div class="col-auto">
          <label for="name">
            Név:
          </label>
          <input
            v-model="newMenu.name"
            class="form-control"
            type="text"
            name="name"
          >
        </div>
        <div class="col-auto">
          <label for="freq">Menü gyakorisága:
          </label>
          <select
            id="freq"
            v-model="newMenu.freq"
            class="form-select"
            name="freq"
          >
            <option
              value="FIX"
              selected
            >
              Fix
            </option>
            <option value="DAILY">
              Napi
            </option>
            <option value="WEAKLY">
              Heti
            </option>
            <option value="MONTLY">
              Havi
            </option>
            <option value="YEARLY">
              Éves
            </option>
          </select>
        </div>
      </div>
      <button
        class="btn"
        :class="['btn-' + auth.getUserColor ]"
        type="button"
        name="save"
        @click="addMenu()"
      >
        Létrehoz
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
          v-for="[i, menu] in menulist"
          :key="i"
        >
          <th scope="row">
            {{ menu.id }}
          </th>
          <td>
            <input
              v-if="menu.isEditing"
              v-model="menu.name"
              type="text"
            >
            <span v-else>
              {{ menu.name }}
            </span>
          </td>
          <td>
            <input
              v-if="menu.isEditing"
              v-model="menu.date"
              type="text"
            >
            <span v-else>
              {{ menu.date }}
            </span>
          </td>
          <td>
            {{ menu.freq }}
          </td>
          <td>
            <button
              v-if="!menu.isEditing"
              type="button"
              name="button"
              class="btn"
              title="Szerkesztés"
              :class="['btn-outline-' + auth.getUserColor ]"
              @click="edit(menu.id)"
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
                @click="updateMenu(menu.id)"
              >
                Mentés
              </button>
              <button
                type="button"
                name="button"
                class="btn"
                title="Mégse"
                :class="['btn-outline-' + auth.getUserColor ]"
                @click="cancelEdit(menu.id)"
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
              @click="deleteMenu(menu.id)"
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
    name: 'VendorMenuManager',
    setup() {
      const auth = useAuth();
      return {
        auth
      }
    },
    data() {
      return {
        menulist: [],
        newMenu: {
          name: "",
          freq: "FIX",
        },
      }
    },
    mounted() {
      this.getMenuList()
    },
    methods: {
      getMenuList: function () {
        axios.get(`http://${window.location.host}/api/menu/${this.$route.params.id}/menu-get`)
          .then(response => {
            let newMenuList = new Map(
              response.data.map(
                item => [item.id, item]
              )
            )
            newMenuList.forEach((item) => {
              item.isEditing = false
            });
            this.menulist = newMenuList
          })
          .catch(e => {
              console.log(e);
          })
      },
      addMenu: function () {
        axios.post(`http://${window.location.host}/api/menu/${this.$route.params.id}/menu-add`, {'data':this.newMenu})
          .then(() => {
            this.getMenuList()
            notify({
              type: "info",
              text: "Menü hozzáadása sikeres!",
            });
          })
          .catch(e => {
              console.log(e);
              notify({
                type: "error",
                text: "Menü hozzáadása nem sikerült!",
              });
          })
      },
      edit: function (menu_id) {
        const item = this.menulist.get(menu_id)
        this.menulist.set(item.id, { ...item, isEditing: true})
      },
      cancelEdit: function (menu_id) {
        const item = this.menulist.get(menu_id)
        this.menulist.set(item.id, { ...item, isEditing: false})
      },
      updateMenu: function (menu_id) {
        const menu = this.menulist.get(menu_id)
        this.menulist.set(menu.id, { ...menu, isEditing: false})
        axios.post(`http://${window.location.host}/api/menu/${this.$route.params.id}/menu-update`, {'data': menu})
          .then(() => {
            this.getMenuList()
            notify({
              type: "info",
              text: "Menü frissítés sikeres!",
            });
          })
          .catch(e => {
              console.log(e);
              notify({
                type: "error",
                text: "Menü frissítés nem sikerült!",
              });
          })
      },
      deleteMenu: function (menu_id) {
        const menu = this.menulist.get(menu_id)
        this.menulist.set(menu.id, { ...menu, isEditing: false})
        axios.post(`http://${window.location.host}/api/menu/${this.$route.params.id}/menu-delete`, {'data': menu})
          .then(() => {
            this.getMenuList()
            notify({
              type: "info",
              text: "Menü törlés sikeres!",
            });
          })
          .catch(e => {
              console.log(e);
              notify({
                type: "error",
                text: "Menü törlés nem sikerült!",
              });
          })
      },
    }
};
</script>

<style scoped>
</style>
