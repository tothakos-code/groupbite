<template>
  <div class="row ms-2 mt-2">
    <div class="col-auto ">
      <div
        class="btn"
        :class="['btn-outline-' + auth.getUserColor ]"
        @click="openAdminHome()"
      >
        vissza
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
      </div>
    </div>
    <h1 class="col d-flex justify-content-start">
      Adminisztráció
    </h1>
    <div class="row row-cols-2 row-cols-sm-3 row-cols-md-4 g-4">
      <div class="col">
        <div
          class="card"
          @click="openAdminVendors()"
        >
          <div class="card-body">
            Üzlet kezelő
          </div>
        </div>
      </div>
      <div class="col">
        <div
          class="card"
          @click="openAdminUsers()"
        >
          <div class="card-body">
            Felhasználók
          </div>
        </div>
      </div>
      <div class="col">
        <div
          class="card"
          @click="openAdminOrders()"
        >
          <div class="card-body">
            Rendelések
          </div>
        </div>
      </div>
      <div class="col">
        <div
          class="card"
          @click="openAdminSettings()"
        >
          <div class="card-body">
            Beállítások
          </div>
        </div>
      </div>
    </div>
  </div>
  <router-view />
</template>

<script>
import { useAuth } from "@/stores/auth";

export default {
    name: "AdminView",
    setup() {
      const auth = useAuth();
      return {
        auth
      }
    },
    data() {
      return {}
    },
    mounted() {
    },
    methods: {
      openAdminHome: function () {
        this.$router.push({ path:`/admin`})
      },
      openAdminOrders: function () {
        this.$router.push({ path:`/admin/orders`})
      },
      openAdminUsers: function () {
        this.$router.push({ path:`/admin`})
      },
      openAdminVendors: function () {
        this.$router.push({ path:`/admin/vendors`})
      },
      openAdminSettings: function () {
        this.$router.push({ path:`/admin/settings`})
      }
    }
};
</script>

<style scoped>
</style>
