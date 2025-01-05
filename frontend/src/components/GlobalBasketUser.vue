<template>
  <v-card
    variant="text"
    :class="auth.isLoggedIn && username === auth.user.username ? 'border-md border-primary' : ''"
  >
    <v-card-title class="bg-header d-flex border-b-sm pe-0">
      <v-row
        no-gutters
        justify="space-between"
      >
        <v-col
          cols="6"
          class="d-inline-block d-flex align-items-center"
        >
          <span
            class=" text-truncate"
            style="max-width: 180px;"
            :title="username"
          >
            {{ username }}
          </span>
          <v-btn
            v-if="copyable && auth.isLoggedIn && username !== auth.user.username"
            varian="text"
            class="ms-2 bg-primary"
            title="Másol"
            @click="orderStore.copy(userId)"
          >
            Másol
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
        </v-col>
        <v-col class="col-6 d-flex justify-content-end">
          <span
            class="me-2"
            :title="basketTotalTitle"
          >{{ basketTotal }} Ft</span>
          <a
            v-if="collapsable"
            class="link-underline link-underline-opacity-0 text-primary"
            data-bs-toggle="collapse"
            :data-bs-target="'#' + userId"
            role="button"
            :aria-expanded="!collapsable || !startCollapsed"
            :aria-controls="userId"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              fill="currentColor"
              class="bi bi-caret-down"
              viewBox="0 0 16 16"
            >
              <path d="M3.204 5h9.592L8 10.481 3.204 5zm-.753.659 4.796 5.48a1 1 0 0 0 1.506 0l4.796-5.48c.566-.647.106-1.659-.753-1.659H3.204a1 1 0 0 0-.753 1.659z" />
            </svg>
          </a>
        </v-col>
      </v-row>
    </v-card-title>
    <v-card-text class="p-0 m-0">
      <div
        :id="collapsable ? userId : false"
        :class="{ show: !collapsable || !startCollapsed, collapse: startCollapsed}"
      >
        <div class="row list-group">
          <v-list-item
            v-for="item in userBasket"
            :key="item.item_id"
            class="justify-content-between border-b-sm"
          >
            <v-row
              no-gutters
            >
              <v-col
                cols="2"
                class="d-flex justify-start"
              >
                <span
                  class="badge rounded-pill bg-secondary border-sm border-error align-self-center"
                >
                  {{ item.quantity }} x
                </span>
              </v-col>
              <v-col
                cols="8"
                class=""
              >
                <span>{{ item.item_name }}</span>
                <span v-if="item.size_name"> ({{ item.size_name }})</span>
              </v-col>
              <v-col
                cols="2"
                class="d-flex justify-end"
              >
                <span class="text-nowrap align-self-center pe-0">{{ item.price }} Ft</span>
              </v-col>
            </v-row>
          </v-list-item>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script>
import { useAuth } from "@/stores/auth";
import { useOrderStore } from "@/stores/order";

export default {
  name: "GlobalBasketUser",
  props: {
    "username":{
      type: String,
      default: ""
    },
    "userId":{
      type: String,
      default: ""
    },
    "userBasket":{
      type: Object,
      default: new Object()
    },
    "orderFee":{
      type: Number,
      default: 0
    },
    "startCollapsed":{
      type: Boolean,
      default: false
    },
    "collapsable":{
      type: Boolean,
      default: true
    },
    "copyable":{
      type: Boolean,
      default: true
    }
  },
  setup() {
    const auth = useAuth();
    const orderStore = useOrderStore();
    return {
      auth,
      orderStore,
    };
  },
  data() {
    return {
      sum: 0
    };
  },
  computed: {
    basketTotal() {
      let sum=0;
      Object.values(this.userBasket).forEach((entry) => {
          sum+= Number(entry.quantity) * Number(entry.price);
      });
      sum += Math.ceil(this.orderFee);
      return sum;
    },
    basketTotalTitle() {
      let sumTitle = ""
      Object.values(this.userBasket).forEach((entry) => {
          sumTitle+= entry.quantity + "*" + entry.price + " Ft + ";
      });
      sumTitle+= Math.ceil(this.orderFee) + " Ft(Szállítási díj) = " + this.basketTotal + " Ft";
      return sumTitle;
    },
  },
}
</script>

<style scoped>

.collapsing {
  width: 100%;
  margin: 0;
}
</style>
