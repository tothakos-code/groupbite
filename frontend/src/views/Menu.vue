<template>
  <div
    class="row d-flex"
  >
    <div class="col-md-7 col-sm-12">
      <div class="row p-2">
        <div class="col col-sm-12 col-xl-auto d-flex justify-content-center justify-content-xl-start">
          <h2>
            {{ vendorTitle }}
          </h2>
        </div>
        <div class="col col-sm-auto col-xl-auto d-flex flex-fill align-items-center justify-content-sm-start justify-content-center justify-content-xl-start">
          <OrderState class="text-truncate my-auto" />
        </div>
        <div class="col col-sm-auto col-xl-auto d-flex justify-content-center justify-content-xl-end align-items-center">
          <div class="">
            <div
              v-if="notificationStatus"
              class="btn me-2"
              :class="['btn-' + auth.getUserColor ]"
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
            </div>
            <div
              v-else
              class="btn me-2"
              :class="['btn-outline-' + auth.getUserColor ]"
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
            </div>
            <a
              v-if="vendorLink !== ''"
              class="btn my-1 me-2"
              :class="['btn-outline-' + auth.getUserColor ]"
              target="_blank"
              :href="vendorLink"
            >Eredeti oldal
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
            </a>
            <TransferPopup />
          </div>
        </div>
      </div>
      <div class="row p-2">
        <MenuList :key="vendorId" />
        <GlobalBasket class="mt-2 d-md-none" />
      </div>
    </div>
    <div class="my-sticky-container col-12 col-md-5 order-first order-md-last">
      <div class="row p-2 ">
        <LocalBasket />
      </div>
      <div class="row p-2 d-none d-md-flex">
        <GlobalBasket />
      </div>
    </div>
  </div>
</template>

<script>
import LocalBasket from "@/components/LocalBasket.vue";
import GlobalBasket from "@/components/GlobalBasket.vue";
import MenuList from "@/components/MenuList.vue";
import TransferPopup from "@/components/TransferPopup.vue";
import OrderState from "@/components/OrderState.vue";
import { useAuth } from "@/stores/auth";
import { useVendorStore } from "@/stores/vendor";

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

    return {
      auth,
      vendorStore
    }
  },
  data() {
    return {
    };
  },
  computed: {
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
