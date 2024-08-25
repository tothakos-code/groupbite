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
        <MenuList
          key="0"
        />
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
import { state } from "@/main";
import { useAuth } from "@/stores/auth";

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

    return {
      auth,
    }
  },
  data() {
    return {
    };
  },
  computed: {
    vendorTitle() {
      return state.selected_vendor.settings.title.value
    },
    vendorLink() {
      return state.selected_vendor.settings.link.value
    },
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
