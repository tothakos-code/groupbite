<template>
  <div class="row ms-2 mt-2">
    <h1 class="col d-flex justify-content-start">
      Üzlet kezelő
    </h1>
    <div class="">
      <v-btn
        class="bg-secondary text-primary me-1 "
        icon
        size="small"
        border="primary thin"
        rounded
        varian="text"
        @click="refreshVendorList()"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          fill="currentColor"
          class="bi bi-arrow-clockwise"
          viewBox="0 0 16 16"
        >
          <path
            fill-rule="evenodd"
            d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2z"
          />
          <path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466" />
        </svg>
      </v-btn>
      <v-btn
        class="bg-secondary text-primary me-1 "
        icon
        size="small"
        border="primary thin"
        rounded
        varian="text"
        @click="addVendor()"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          fill="currentColor"
          class="bi bi-building-add"
          viewBox="0 0 16 16"
        >
          <path d="M12.5 16a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7m.5-5v1h1a.5.5 0 0 1 0 1h-1v1a.5.5 0 0 1-1 0v-1h-1a.5.5 0 0 1 0-1h1v-1a.5.5 0 0 1 1 0" />
          <path d="M2 1a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v6.5a.5.5 0 0 1-1 0V1H3v14h3v-2.5a.5.5 0 0 1 .5-.5H8v4H3a1 1 0 0 1-1-1z" />
          <path d="M4.5 2a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5zm3 0a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5zm3 0a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5zm-6 3a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5zm3 0a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5zm3 0a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5zm-6 3a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5zm3 0a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5z" />
        </svg>
      </v-btn>
    </div>
    <div class="row ms-2">
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
              aktív
            </th>
            <th scope="col">
              Műveletek
            </th>
          </tr>
        </thead>
        <tbody class="table-group-divider">
          <tr
            v-for="vendor,i in allVendorList"
            :key="i"
          >
            <th scope="row">
              {{ i+1 }}
            </th>
            <td>
              {{ vendor.name }}
            </td>
            <td>
              {{ vendor.active }}
            </td>
            <td>
              <div
                class="btn text-primary"
                title="Üzlet elérhetőség ki/be kapcsolása"
                @click="toggleActivation(vendor)"
              >
                <svg
                  v-if="vendor.active"
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
                class="btn text-primary"
                title="Üzlet beállítások"
                @click="openVendorConfiguration(vendor.id)"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  fill="currentColor"
                  class="bi bi-gear-fill"
                  viewBox="0 0 16 16"
                >
                  <path d="M9.405 1.05c-.413-1.4-2.397-1.4-2.81 0l-.1.34a1.464 1.464 0 0 1-2.105.872l-.31-.17c-1.283-.698-2.686.705-1.987 1.987l.169.311c.446.82.023 1.841-.872 2.105l-.34.1c-1.4.413-1.4 2.397 0 2.81l.34.1a1.464 1.464 0 0 1 .872 2.105l-.17.31c-.698 1.283.705 2.686 1.987 1.987l.311-.169a1.464 1.464 0 0 1 2.105.872l.1.34c.413 1.4 2.397 1.4 2.81 0l.1-.34a1.464 1.464 0 0 1 2.105-.872l.31.17c1.283.698 2.686-.705 1.987-1.987l-.169-.311a1.464 1.464 0 0 1 .872-2.105l.34-.1c1.4-.413 1.4-2.397 0-2.81l-.34-.1a1.464 1.464 0 0 1-.872-2.105l.17-.31c.698-1.283-.705-2.686-1.987-1.987l-.311.169a1.464 1.464 0 0 1-2.105-.872zM8 10.93a2.929 2.929 0 1 1 0-5.86 2.929 2.929 0 0 1 0 5.858z" />
                </svg>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { useAuth } from "@/stores/auth";
import { useVendorStore } from "@/stores/vendor";

export default {
    name: "AdminVendors",
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
        allVendorList: []
      }
    },
    mounted() {
      this.refreshVendorList()
    },
    methods: {
      openAdminHome: function () {
        this.$router.push({ path:`/admin`})
      },
      refreshVendorList: function () {
        this.vendorStore.fetch()
          .then(response => {
            this.allVendorList = response.data.data
          })
      },
      toggleActivation: function (to) {
        if (to.active) {
          this.vendorStore.deactivate(to.id).then(() => {
            this.refreshVendorList();
          })
        } else {
          this.vendorStore.activate(to.id).then(() => {
            this.refreshVendorList();
          })
        }
      },
      openVendorConfiguration: function (id) {
        this.$router.push({ path:`/admin/${id}/config`})
      },
      addVendor: function () {
        this.$router.push({ path:`/admin/add`})
      }
    }
};
</script>

<style scoped>
</style>
