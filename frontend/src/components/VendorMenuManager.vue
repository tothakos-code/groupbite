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
            <option value="WEEKLY">
              Heti
            </option>
            <option value="MONTHLY">
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
      <button
        class="btn ms-2"
        :class="['btn-' + auth.getUserColor ]"
        type="button"
        name="save"
        @click="openImportPopup()"
      >
        Importálás
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
            Aktív
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
            {{ menu.active }}
          </td>
          <td>
            <div
              class="btn"
              :class="['text-' + auth.getUserColor ]"
              title="Üzlet elérhetőség ki/be kapcsolása"
              @click="toggleActivation(menu)"
            >
              <svg
                v-if="menu.active"
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                fill="currentColor"
                class="bi bi-toggle-on"
                viewBox="0 0 16 16"
              >
                <path d="M5 3a5 5 0 0 0 0 10h6a5 5 0 0 0 0-10zm6 9a4 4 0 1 1 0-8 4 4 0 0 1 0 8" />
              </svg>
              <svg
                v-else
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                fill="currentColor"
                class="bi bi-toggle-off"
                viewBox="0 0 16 16"
              >
                <path d="M11 4a4 4 0 0 1 0 8H8a5 5 0 0 0 2-4 5 5 0 0 0-2-4zm-6 8a4 4 0 1 1 0-8 4 4 0 0 1 0 8M0 8a5 5 0 0 0 5 5h6a5 5 0 0 0 0-10H5a5 5 0 0 0-5 5" />
              </svg>
            </div>
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
            <button
              type="button"
              name="button"
              class="btn"
              title="Duplikál"
              :class="['btn-outline-' + auth.getUserColor ]"
              @click="duplicateMenu(menu.id)"
            >
              Duplikál
            </button>
          </td>
        </tr>
      </tbody>
    </table>
    <Popup
      title="Menü importlálsa JSON fájlból"
      :show-modal="showImportPopup"
      confirm-text="Küldés"
      @cancel="showImportPopup=false"
      @confirm="submitJsonFile()"
    >
      <p>
        A JSON fájlnak követnie kell egy meghatárotzott struktúrát. Bővebben lásd a dokumentációban(bal alsó sarok <span class="fst-italic">i</span> ikon).
      </p>
      <div class="mb-3">
        <label
          for="importJson"
          class="form-label"
        >JSON fájl:</label>
        <input
          id="importJson"
          class="form-control"
          type="file"
          @change="handleFileUpload( $event )"
        >
      </div>
    </Popup>
  </div>
</template>

<script>
import axios from "axios";
import { useAuth } from "@/stores/auth";
import { useMenu } from "@/stores/menu";
import Popup from "./Popup.vue";
import { notify } from "@kyvg/vue3-notification";

export default {
    name: "VendorMenuManager",
    components: {
      Popup
    },
    setup() {
      const auth = useAuth();
      const menuStore = useMenu();
      return {
        auth,
        menuStore
      }
    },
    data() {
      return {
        menulist: [],
        newMenu: {
          name: "",
          freq: "FIX",
        },
        showImportPopup: false,
        json_file: ""
      }
    },
    mounted() {
      this.getMenuList()
    },
    methods: {
      openImportPopup: function () {
        this.showImportPopup = true;
      },
      submitJsonFile: function () {
        let formData = new FormData();
        formData.append("file", this.file);
        axios.post( `http://${window.location.host}/api/menu/import/${this.$route.params.id}`,
          formData,
          {
            headers: {
                "Content-Type": "multipart/form-data"
            }
          }
        ).then(() => {
          console.log("SUCCESS file upload!!");
          this.showImportPopup=false
          this.getMenuList()
          notify({
            type: "info",
            text: "Menü importálás sikeres!",
          });
        })
        .catch(e => {
          console.log("FAILURE in file upload!!");
          console.log(e);
          notify({
            type: "error",
            text: "Menü importálása nem sikerült!",
          });
        });
      },
      handleFileUpload: function (event) {
        const file = event.target.files[0];
        if (file && file.type === "application/json") {
          const reader = new FileReader();
          reader.onload = (e) => {
            try {
              const json = JSON.parse(e.target.result);
              console.log("Valid JSON:", json);
              this.file = event.target.files[0];
            } catch (error) {
              console.log("Invalid JSON:", error);
              notify({
                type: "error",
                text: "Helytelen JSON fájl: " + error,
              })
            }
          };
          reader.readAsText(file);
        } else {
          console.log("Only .json files are allowed");
        }
      },
      toggleActivation: function (to) {
        let result;
        if (to.active) {
          result = this.menuStore.deactivate(to.id)
        } else {
          result = this.menuStore.activate(to.id)
        }

        result.then(response => {
          if (response.status === 200) {
            this.getMenuList()
          }
        })
      },
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
        this.newMenu.vendor_id = this.$route.params.id
        this.menuStore.add(this.$route.params.id, {"data":this.newMenu} )
          .then(response => {
            if (response.status === 201) {
              this.getMenuList()
            }
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
        delete menu["isEditing"];
        this.menuStore.update(menu_id, {"data": menu} )
          .then(response => {
            if (response.status === 200) {
              this.getMenuList()
            }
          })
      },
      deleteMenu: function (menu_id) {
        const menu = this.menulist.get(menu_id)
        this.menulist.set(menu.id, { ...menu, isEditing: false})
        delete menu["isEditing"];
        this.menuStore.delete(menu_id, {"data": menu} )
          .then(response => {
            if (response.status === 200) {
              this.getMenuList()
            }
          })
      },
      duplicateMenu: function (menu_id) {
        const menu = this.menulist.get(menu_id)
        this.menulist.set(menu.id, { ...menu, isEditing: false})
        delete menu["isEditing"];
        this.menuStore.duplicate(menu_id, {"data": menu} )
          .then(response => {
            if (response.status === 200) {
              this.getMenuList()
            }
          })
      },
    }
};
</script>

<style scoped>
</style>
