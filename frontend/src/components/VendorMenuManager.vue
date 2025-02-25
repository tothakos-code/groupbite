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
      </div>
      <v-btn
        class="bg-primary"
        type="button"
        name="save"
        @click="addMenu()"
      >
        Létrehoz
      </v-btn>
      <v-btn
        class="ms-2 bg-primary"
        type="button"
        name="save"
        @click="openImportPopup()"
      >
        Importálás
      </v-btn>
    </div>
    <div
      class="row mt-2"
    >
      <div class="col-2">
        <label for="itemName">
          Keresés:
        </label>
        <input
          v-model.trim="searchString"
          type="text"
          name="itemName"
          class="form-control"
        >
      </div>
      <v-btn
        class="bg-primary align-self-end col-auto"
        type="button"
        name="save"
        @click="search()"
      >
        keresés
      </v-btn>
    </div>
  </div>
  <div class="">
    <table class="table table-striped table-hover ">
      <thead>
        <tr class="">
          <th
            scope="col"
            class="col-auto"
          >
            #
          </th>
          <th
            scope="col"
            class="col-2"
          >
            Név
          </th>
          <th
            scope="col"
            class="col-2"
          >
            Dátumtól
          </th>
          <th
            scope="col"
            class="col-2"
          >
            Dátumig
          </th>
          <th
            scope="col"
            class="col-auto"
          >
            Aktív
          </th>
          <th
            scope="col"
            class="col-5"
          >
            Műveletek
          </th>
        </tr>
      </thead>
      <tbody
        v-if="!isLoading"
        class="table-group-divider"
      >
        <tr
          v-for="[i, menu] in menulist"
          :key="i"
          class=""
        >
          <th
            scope="row"
            class="col-auto"
          >
            {{ menu.id }}
          </th>
          <td class="col-2">
            <input
              v-if="menu.isEditing"
              v-model="menu.name"
              class="form-control"
              type="text"
            >
            <span v-else>
              {{ menu.name }}
            </span>
          </td>
          <td class="col-2">
            <input
              v-if="menu.isEditing"
              v-model="menu.from_date"
              class="form-control"
              type="text"
            >
            <span v-else>
              {{ menu.from_date }}
            </span>
          </td>
          <td class="col-2">
            <input
              v-if="menu.isEditing"
              v-model="menu.to_date"
              class="form-control"
              type="text"
            >
            <span v-else>
              {{ menu.to_date }}
            </span>
          </td>
          <td class="col-auto">
            {{ menu.active }}
          </td>
          <td class="col row">
            <div
              class="btn col-auto text-primary"
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
            <div
              v-if="!menu.isEditing"
              class="col-auto"
            >
              <v-btn
                type="button"
                name="button"
                title="Szerkesztés"
                class="bg-primary me-1 mt-1"
                icon
                size="small"
                border="primary thin"
                rounded
                varian="text"
                @click="edit(menu.id)"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  fill="currentColor"
                  class="bi bi-pen"
                  viewBox="0 0 16 16"
                >
                  <path d="m13.498.795.149-.149a1.207 1.207 0 1 1 1.707 1.708l-.149.148a1.5 1.5 0 0 1-.059 2.059L4.854 14.854a.5.5 0 0 1-.233.131l-4 1a.5.5 0 0 1-.606-.606l1-4a.5.5 0 0 1 .131-.232l9.642-9.642a.5.5 0 0 0-.642.056L6.854 4.854a.5.5 0 1 1-.708-.708L9.44.854A1.5 1.5 0 0 1 11.5.796a1.5 1.5 0 0 1 1.998-.001m-.644.766a.5.5 0 0 0-.707 0L1.95 11.756l-.764 3.057 3.057-.764L14.44 3.854a.5.5 0 0 0 0-.708z" />
                </svg>
              </v-btn>
            </div>
            <div
              v-if="menu.isEditing"
              class="col-auto"
            >
              <v-btn
                type="button"
                name="button"
                title="Mentés"
                class="bg-primary me-1 mt-1"
                icon
                size="small"
                border="primary thin"
                rounded
                varian="text"
                @click="updateMenu(menu.id)"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  fill="currentColor"
                  class="bi bi-floppy"
                  viewBox="0 0 16 16"
                >
                  <path d="M11 2H9v3h2z" />
                  <path d="M1.5 0h11.586a1.5 1.5 0 0 1 1.06.44l1.415 1.414A1.5 1.5 0 0 1 16 2.914V14.5a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 0 14.5v-13A1.5 1.5 0 0 1 1.5 0M1 1.5v13a.5.5 0 0 0 .5.5H2v-4.5A1.5 1.5 0 0 1 3.5 9h9a1.5 1.5 0 0 1 1.5 1.5V15h.5a.5.5 0 0 0 .5-.5V2.914a.5.5 0 0 0-.146-.353l-1.415-1.415A.5.5 0 0 0 13.086 1H13v4.5A1.5 1.5 0 0 1 11.5 7h-7A1.5 1.5 0 0 1 3 5.5V1H1.5a.5.5 0 0 0-.5.5m3 4a.5.5 0 0 0 .5.5h7a.5.5 0 0 0 .5-.5V1H4zM3 15h10v-4.5a.5.5 0 0 0-.5-.5h-9a.5.5 0 0 0-.5.5z" />
                </svg>
              </v-btn>
            </div>
            <div
              v-if="menu.isEditing"
              class="col-auto"
            >
              <v-btn
                type="button"
                name="button"
                title="Mégse"
                class="bg-primary me-1 mt-1"
                icon
                size="small"
                border="primary thin"
                rounded
                varian="text"
                @click="cancelEdit(menu.id)"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  fill="currentColor"
                  class="bi bi-x"
                  viewBox="0 0 16 16"
                >
                  <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708" />
                </svg>
              </v-btn>
            </div>
            <div
              v-if="!menu.isEditing"
              class="col-auto"
            >
              <v-btn
                type="button"
                name="button"
                title="Törlés"
                class="bg-primary me-1 mt-1"
                icon
                size="small"
                border="primary thin"
                rounded
                varian="text"
                @click="deleteMenu(menu.id)"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  fill="currentColor"
                  class="bi bi-trash"
                  viewBox="0 0 16 16"
                >
                  <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z" />
                  <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z" />
                </svg>
              </v-btn>
            </div>
            <div
              v-if="!menu.isEditing"
              class="col-auto"
            >
              <v-btn
                type="button"
                name="button"
                title="Duplikál"
                class="bg-primary me-1 mt-1"
                icon
                size="small"
                border="primary thin"
                rounded
                varian="text"
                @click="duplicateMenu(menu.id)"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  fill="currentColor"
                  class="bi bi-copy"
                  viewBox="0 0 16 16"
                >
                  <path
                    fill-rule="evenodd"
                    d="M4 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2zm2-1a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1zM2 5a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1v-1h1v1a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h1v1z"
                  />
                </svg>
              </v-btn>
            </div>
            <div
              v-if="!menu.isEditing"
              class="col-auto"
            >
              <v-btn
                type="button"
                name="button"
                title="Items"
                class="bg-primary me-1 mt-1"
                icon
                size="small"
                border="primary thin"
                rounded
                varian="text"
                @click="openItemManger(menu.id)"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  fill="currentColor"
                  class="bi bi-menu-button-wide"
                  viewBox="0 0 16 16"
                >
                  <path d="M2 12a.5.5 0 00.5.5h6a.5.5 0 000-1h-6a.5.5 0 00-.5.5Zm0-5a.5.5 0 00.5.5h9a.5.5 0 000-1h-9A.5.5 0 002 7M1 4V2A1 1 0 012 1H14a1 1 0 011 1V4Zm14 6v3a1 1 0 01-1 1H2A1 1 0 011 13V10M1 5H15V9H1ZM0 13a2 2 0 002 2H14a2 2 0 002-2V2A2 2 0 0014 0H2A2 2 0 000 2ZM2 2.5a.5.5 0 00.5.5h5.5a.5.5 0 000-1h-5.5A.5.5 0 002 2.5" />
                </svg>
              </v-btn>
            </div>
          </td>
        </tr>
      </tbody>
      <div
        v-else
        class="row text-center"
      >
        <div
          class="spinner-border"
          role="status"
        >
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
    </table>
    <Paginator
      :total-pages="Math.ceil(totalCount/limit)"
      :current-page="currentPage"
      :range="5"
      @page-change="handlePageChange"
    />

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
import { useAuth } from "@/stores/auth";
import { useMenuStore } from "@/stores/menu";
import Popup from "./Popup.vue";
import Paginator from "./Paginator.vue";
import { notify } from "@kyvg/vue3-notification";
import { useVendorStore } from "@/stores/vendor";


export default {
    name: "VendorMenuManager",
    components: {
      Popup,
      Paginator
    },
    setup() {
      const auth = useAuth();
      const menuStore = useMenuStore();
      const vendorStore = useVendorStore();
      return {
        auth,
        menuStore,
        vendorStore
      }
    },
    data() {
      return {
        menulist: [],
        newMenu: {
          name: "",
        },
        isLoading: true,
        showImportPopup: false,
        searchString: "",
        json_file: "",
        limit: 10,
        currentPage: 1,
        totalCount: 0
      }
    },
    mounted() {
      this.getMenuList()
    },
    methods: {
      handlePageChange(page) {
        this.currentPage = page;
        this.getMenuList()
      },
      search() {
        this.getMenuList()
      },
      openImportPopup() {
        this.showImportPopup = true;
      },
      submitJsonFile() {
        let formData = new FormData();
        formData.append("file", this.file);
        this.vendorStore.import(this.$route.params.id, formData)
        .then(response => {
          if (response.status === 201) {
            this.showImportPopup=false
            this.getMenuList()
          }
        })
      },
      handleFileUpload(event) {
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
      toggleActivation(to) {
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
      getMenuList() {
        this.vendorStore.fetchMenus(this.$route.params.id,{
            "search": this.searchString,
            "limit": this.limit,
            "page": this.currentPage
          })
          .then(response => {
            let newMenuList = new Map(
              response.data.data.menus.map(
                item => [item.id, item]
              )
            );
            newMenuList.forEach((item) => {
              item.isEditing = false;
            });
            this.currentPage = response.data.data.page;
            this.limit = response.data.data.limit;
            this.totalCount = response.data.data.total_count;
            this.menulist = newMenuList;
            this.isLoading = false;
          })
          .catch(e => {
              console.log(e);
          })
      },
      addMenu() {
        this.newMenu.vendor_id = this.$route.params.id
        this.menuStore.add(this.newMenu)
          .then(response => {
            if (response.status === 201) {
              this.getMenuList()
            }
          })
      },
      edit(menu_id) {
        const item = this.menulist.get(menu_id)
        this.menulist.set(item.id, { ...item, isEditing: true})
      },
      cancelEdit(menu_id) {
        const item = this.menulist.get(menu_id)
        this.menulist.set(item.id, { ...item, isEditing: false})
      },
      updateMenu(menu_id) {
        const menu = this.menulist.get(menu_id)
        if (!menu.from_date) {
          delete menu["from_date"]
        }
        if (!menu.to_date) {
          delete menu["to_date"]
        }
        this.menulist.set(menu.id, { ...menu, isEditing: false})
        delete menu["isEditing"];
        this.menuStore.update(menu_id, menu )
          .then(response => {
            if (response.status === 200) {
              this.getMenuList()
            }
          })
      },
      deleteMenu(menu_id) {
        const menu = this.menulist.get(menu_id)
        this.menulist.set(menu.id, { ...menu, isEditing: false})
        delete menu["isEditing"];
        this.menuStore.delete(menu_id)
          .then(response => {
            if (response.status === 200) {
              this.getMenuList()
            }
          })
      },
      duplicateMenu(menu_id) {
        const menu = this.menulist.get(menu_id)
        this.menulist.set(menu.id, { ...menu, isEditing: false})
        delete menu["isEditing"];
        this.menuStore.duplicate(menu_id, menu )
          .then(response => {
            if (response.status === 200) {
              this.getMenuList()
            }
          })
      },
      openItemManger(menu_id) {
        this.$router.push({ path:`/admin/${this.$route.params.id}/config/${menu_id}`})
      }
    }
};
</script>

<style scoped>
</style>
