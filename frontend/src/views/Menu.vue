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
        <div class="row p-2">
          <div class="col col-sm-12 col-xl-auto d-flex justify-content-center justify-content-xl-start">
            <h2>
              {{ vendorTitle }}
            </h2>
          </div>
          <div class="col col-sm-auto col-xl-auto d-flex flex-fill align-items-center justify-content-sm-start justify-content-center justify-content-xl-start">
            <OrderState

              class="text-truncate my-auto"
            />
          </div>
          <div class="col col-sm-auto col-xl-auto d-flex justify-content-center justify-content-xl-end align-items-center">
            <div class="">
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <v-btn
                    v-if="notificationStatus"
                    v-bind="props"
                    class="bg-primary  me-2"
                    icon
                    size="small"
                    border="primary thin"
                    rounded
                    varian="text"
                    @click="unsubscribe()"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="16"
                      height="16"
                      fill="currentColor"
                      class="bi bi-bell"
                      viewBox="0 0 16 16"
                    >
                      <path d="M8 16a2 2 0 0 0 2-2H6a2 2 0 0 0 2 2M8 1.918l-.797.161A4 4 0 0 0 4 6c0 .628-.134 2.197-.459 3.742-.16.767-.376 1.566-.663 2.258h10.244c-.287-.692-.502-1.49-.663-2.258C12.134 8.197 12 6.628 12 6a4 4 0 0 0-3.203-3.92zM14.22 12c.223.447.481.801.78 1H1c.299-.199.557-.553.78-1C2.68 10.2 3 6.88 3 6c0-2.42 1.72-4.44 4.005-4.901a1 1 0 1 1 1.99 0A5 5 0 0 1 13 6c0 .88.32 4.2 1.22 6" />
                    </svg>
                  </v-btn>
                  <v-btn
                    v-else
                    v-bind="props"
                    class="bg-primary me-2"
                    icon
                    size="small"
                    border="primary sm"
                    rounded
                    varian="text"
                    @click="subscribe()"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="16"
                      height="16"
                      fill="currentColor"
                      class="bi bi-bell-slash"
                      viewBox="0 0 16 16"
                    >
                      <path d="M5.164 14H15c-.299-.199-.557-.553-.78-1-.9-1.8-1.22-5.12-1.22-6q0-.396-.06-.776l-.938.938c.02.708.157 2.154.457 3.58.161.767.377 1.566.663 2.258H6.164zm5.581-9.91a4 4 0 0 0-1.948-1.01L8 2.917l-.797.161A4 4 0 0 0 4 7c0 .628-.134 2.197-.459 3.742q-.075.358-.166.718l-1.653 1.653q.03-.055.059-.113C2.679 11.2 3 7.88 3 7c0-2.42 1.72-4.44 4.005-4.901a1 1 0 1 1 1.99 0c.942.19 1.788.645 2.457 1.284zM10 15a2 2 0 1 1-4 0zm-9.375.625a.53.53 0 0 0 .75.75l14.75-14.75a.53.53 0 0 0-.75-.75z" />
                    </svg>
                  </v-btn>
                </template>
                <span>Üzlet értesítés {{ notificationStatus ? "ki" : "be" }}kapcsolása</span>
              </v-tooltip>
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <v-btn
                    v-if="vendorLink !== ''"
                    v-bind="props"
                    varian="text"
                    class="my-1 me-2 text-primary bg-secondary"
                    title="Másol"
                    border="primary thin"
                    target="_blank"
                    :href="vendorLink"
                  >
                    Eredeti oldal
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="16"
                      height="16"
                      fill="currentColor"
                      class="bi bi-box-arrow-up-right mb-1"
                      viewBox="0 0 16 16"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M8.636 3.5a.5.5 0 0 0-.5-.5H1.5A1.5 1.5 0 0 0 0 4.5v10A1.5 1.5 0 0 0 1.5 16h10a1.5 1.5 0 0 0 1.5-1.5V7.864a.5.5 0 0 0-1 0V14.5a.5.5 0 0 1-.5.5h-10a.5.5 0 0 1-.5-.5v-10a.5.5 0 0 1 .5-.5h6.636a.5.5 0 0 0 .5-.5"
                      />
                      <path
                        fill-rule="evenodd"
                        d="M16 .5a.5.5 0 0 0-.5-.5h-5a.5.5 0 0 0 0 1h3.793L6.146 9.146a.5.5 0 1 0 .708.708L15 1.707V5.5a.5.5 0 0 0 1 0z"
                      />
                    </svg>
                  </v-btn>
                </template>
                <span>Eredeti étterem oldala megnyitás új lapon</span>
              </v-tooltip>

              <TransferPopup />
            </div>
          </div>
        </div>
        <v-row class="row m-0 p-2">
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
          class="row m-0"
        >
          <LocalBasket />
        </v-row>

        <v-row class="row m-0 mt-2">
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
import TransferPopup from "@/components/TransferPopup.vue";
import OrderState from "@/components/OrderState.vue";
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
    OrderState,
    TransferPopup
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
    vendorId() {
      return this.vendorStore.selectedVendor.id
    },
    vendorTitle() {
      return this.vendorStore.selectedVendor.settings.title.value
    },
    vendorLink() {
      return this.vendorStore.selectedVendor.settings.link.value
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
    subscribe: function () {
      this.vendorStore.subscribe()
    },
    unsubscribe: function () {
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
