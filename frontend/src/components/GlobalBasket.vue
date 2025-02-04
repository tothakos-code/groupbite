<template>
  <v-card class="border-sm w-100">
    <v-card-title class="align-items-center bg-header border-b-sm p-1">
      <v-row
        align-content="center"
        justify="space-between"
        class="m-0"
      >
        <v-col
          cols="auto"
          class="my-auto"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="28"
            height="28"
            fill="currentColor"
            class="bi bi-cart4 mb-1"
            viewBox="0 0 16 16"
          >
            <path d="M0 2.5A.5.5 0 0 1 .5 2H2a.5.5 0 0 1 .485.379L2.89 4H14.5a.5.5 0 0 1 .485.621l-1.5 6A.5.5 0 0 1 13 11H4a.5.5 0 0 1-.485-.379L1.61 3H.5a.5.5 0 0 1-.5-.5zM3.14 5l.5 2H5V5H3.14zM6 5v2h2V5H6zm3 0v2h2V5H9zm3 0v2h1.36l.5-2H12zm1.11 3H12v2h.61l.5-2zM11 8H9v2h2V8zM8 8H6v2h2V8zM5 8H3.89l.5 2H5V8zm0 5a1 1 0 1 0 0 2 1 1 0 0 0 0-2zm-2 1a2 2 0 1 1 4 0 2 2 0 0 1-4 0zm9-1a1 1 0 1 0 0 2 1 1 0 0 0 0-2zm-2 1a2 2 0 1 1 4 0 2 2 0 0 1-4 0z" />
          </svg>
        </v-col>
        <v-col class="col-5 text-start my-auto d-none d-sm-inline d-md-none d-lg-inline">
          <span class="fs-2 text-nowrap">Közös kosár</span>
        </v-col>
        <v-col
          cols="auto"
          class="my-auto p-0 mx-1 ms-auto"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            fill="currentColor"
            class="bi bi-cash-stack mb-1 me-1"
            viewBox="0 0 16 16"
          >
            <path d="M1 3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1H1zm7 8a2 2 0 1 0 0-4 2 2 0 0 0 0 4z" />
            <path d="M0 5a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H1a1 1 0 0 1-1-1V5zm3 0a2 2 0 0 1-2 2v4a2 2 0 0 1 2 2h10a2 2 0 0 1 2-2V7a2 2 0 0 1-2-2H3z" />
          </svg>
          <span>{{ orderStore.totalSum }} Ft</span>
        </v-col>
        <v-col
          cols="auto"
          class="my-auto mx-2 p-0"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            fill="currentColor"
            class="bi bi-people mb-1 me-1"
            viewBox="0 0 16 16"
          >
            <path d="M15 14s1 0 1-1-1-4-5-4-5 3-5 4 1 1 1 1h8Zm-7.978-1A.261.261 0 0 1 7 12.996c.001-.264.167-1.03.76-1.72C8.312 10.629 9.282 10 11 10c1.717 0 2.687.63 3.24 1.276.593.69.758 1.457.76 1.72l-.008.002a.274.274 0 0 1-.014.002H7.022ZM11 7a2 2 0 1 0 0-4 2 2 0 0 0 0 4Zm3-2a3 3 0 1 1-6 0 3 3 0 0 1 6 0ZM6.936 9.28a5.88 5.88 0 0 0-1.23-.247A7.35 7.35 0 0 0 5 9c-4 0-5 3-5 4 0 .667.333 1 1 1h4.216A2.238 2.238 0 0 1 5 13c0-1.01.377-2.042 1.09-2.904.243-.294.526-.569.846-.816ZM4.92 10A5.493 5.493 0 0 0 4 13H1c0-.26.164-1.03.76-1.724.545-.636 1.492-1.256 3.16-1.275ZM1.5 5.5a3 3 0 1 1 6 0 3 3 0 0 1-6 0Zm3-2a2 2 0 1 0 0 4 2 2 0 0 0 0-4Z" />
          </svg>
          <span>{{ orderStore.userCount }} fő</span>
        </v-col>
      </v-row>
    </v-card-title>
    <div
      v-for="(user_entry) in orderStore.basket"
      :key="user_entry.id"
      class="mt-1 mb-1"
    >
      <GlobalBasketUser
        :username="user_entry.username"
        :user-id="user_entry.user_id"
        :user-basket="user_entry.items"
        :order-fee="transportFee"
        :collapsable="false"
      />
    </div>
  </v-card>
</template>

<script>
import GlobalBasketUser from "./GlobalBasketUser.vue"
import { useOrderStore } from "@/stores/order";

export default {
  name: "GlobalBasket",
  components: {
    GlobalBasketUser
  },
  setup() {
    const orderStore = useOrderStore();
    return {
      orderStore
    }
  },
  computed: {
    transportFee() {
      return this.orderStore.transportFeePerPerson
    },
  }
}
</script>

<style>
</style>
