<template>
  <v-container
    :fluid="true"
  >
    <v-row>
      <v-col
        v-show="mobileNav == 'menu' || lgAndUp"
        cols="12"
        md="7"
        class="p-0 mt-2"
      >
        <MenuHeader
          :vendor-title="vendorTitle"
          :vendor-settings="vendorSettings"
          :user-count="userCount"
          :vendor-link="vendorLink"
          :notification-status="notificationStatus"
          @subscribe="handleSubscribe"
          @unsubscribe="handleUnsubscribe"
        />
        <v-row
          class="m-0 p-2"
        >
          <MenuList :key="vendorId" />
        </v-row>
      </v-col>
      <v-col
        v-show="mobileNav == 'basket' || lgAndUp"
        cols="12"
        md="5"
        class="mt-2 p-1 pe-0"
      >
        <v-row
          class="m-0"
        >
          <LocalBasket />
        </v-row>

        <v-row class="m-0 mt-2">
          <GlobalBasket />
        </v-row>
      </v-col>
    </v-row>
    <v-bottom-navigation
      v-model="mobileNav"
      class="hidden-md-and-up"
      color="teal"
      grow
    >
      <v-btn value="menu">
        <v-icon>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            fill="currentColor"
            class="bi bi-menu-button-wide"
            viewBox="0 0 16 16"
          >
            <path d="M2 12a.5.5 0 00.5.5h6a.5.5 0 000-1h-6a.5.5 0 00-.5.5Zm0-5a.5.5 0 00.5.5h9a.5.5 0 000-1h-9A.5.5 0 002 7M1 4V2A1 1 0 012 1H14a1 1 0 011 1V4Zm14 6v3a1 1 0 01-1 1H2A1 1 0 011 13V10M1 5H15V9H1ZM0 13a2 2 0 002 2H14a2 2 0 002-2V2A2 2 0 0014 0H2A2 2 0 000 2ZM2 2.5a.5.5 0 00.5.5h5.5a.5.5 0 000-1h-5.5A.5.5 0 002 2.5" />
          </svg>
        </v-icon>

        Menü
      </v-btn>

      <v-btn value="basket">
        <v-icon>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            fill="currentColor"
            class="bi bi-cart4"
            viewBox="0 0 16 16"
          >
            <path d="M0 2.5A.5.5 0 0 1 .5 2H2a.5.5 0 0 1 .485.379L2.89 4H14.5a.5.5 0 0 1 .485.621l-1.5 6A.5.5 0 0 1 13 11H4a.5.5 0 0 1-.485-.379L1.61 3H.5a.5.5 0 0 1-.5-.5M3.14 5l.5 2H5V5zM6 5v2h2V5zm3 0v2h2V5zm3 0v2h1.36l.5-2zm1.11 3H12v2h.61zM11 8H9v2h2zM8 8H6v2h2zM5 8H3.89l.5 2H5zm0 5a1 1 0 1 0 0 2 1 1 0 0 0 0-2m-2 1a2 2 0 1 1 4 0 2 2 0 0 1-4 0m9-1a1 1 0 1 0 0 2 1 1 0 0 0 0-2m-2 1a2 2 0 1 1 4 0 2 2 0 0 1-4 0" />
          </svg>
          <span
            class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-teal-lighten-3"
            style="font-size: 10px"
          >
            {{ itemCount }}
            <span class="visually-hidden">unread messages</span>
          </span>
        </v-icon>

        Kosár
      </v-btn>
    </v-bottom-navigation>
  </v-container>
</template>

<script>
import LocalBasket from "@/components/LocalBasket.vue";
import GlobalBasket from "@/components/GlobalBasket.vue";
import MenuList from "@/components/MenuList.vue";
import MenuHeader from '@/components/menu/MenuHeader.vue'
import { useAuth } from "@/stores/auth";
import { useVendorStore } from "@/stores/vendor";
import { useOrderStore } from "@/stores/order";
import { useDisplay } from 'vuetify'

export default {
  name: "MenuView",
  components: {
    LocalBasket,
    GlobalBasket,
    MenuList,
    MenuHeader,
  },
  setup() {
    const auth = useAuth();
    const vendorStore = useVendorStore();
    const orderStore = useOrderStore();
    const { lgAndUp } = useDisplay();

    return {
      auth,
      lgAndUp,
      orderStore,
      vendorStore
    }
  },
  data() {
    return {
      mobileNav: "menu"
    };
  },
  computed: {
    itemCount() {
      return this.orderStore.userBasket.length
    },
    userCount() {
      return this.orderStore.userCount
    },
    vendorId() {
      return this.vendorStore.selectedVendor.id
    },
    vendorTitle() {
      return this.vendorStore.selectedVendor.settings.title.value
    },
    vendorLink() {
      return this.vendorStore.selectedVendor.settings.link.value
    },
    vendorSettings() {
      return this.vendorStore.selectedVendor.settings
    },
    notificationStatus() {
      let response = false;
      if (!this.auth.isLoggedIn) {
        return response;
      }
      Object.values(this.auth.user.notifications).forEach(notification => {
        if(notification.vendor_id == this.vendorStore.selectedVendor.id) {
          response = true;
        }
      })
      return response;
    },
  },
  methods: {
    handleSubscribe: function () {
      this.vendorStore.subscribe()
    },
    handleUnsubscribe: function () {
      this.vendorStore.unsubscribe()
    }
  }
};
</script>

<style scoped>
@media only screen and (max-width: 768px){
  .my-sticky-container {
        position: sticky;
        top: 5px;
        z-index: 1;
  }
 }
</style>
