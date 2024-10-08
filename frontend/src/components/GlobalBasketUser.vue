<template>
  <div
    class="card"
    :class="auth.isLoggedIn && username === auth.user.username ? 'border border-2 border-'+ auth.getUserColor : ''"
  >
    <div class="card-header row d-flex pe-0">
      <div class="col-6 d-inline-block d-flex align-items-center">
        <span
          class=" text-truncate"
          style="max-width: 120px;"
        >
          {{ username }}
        </span>
        <a
          v-if="copyable && auth.isLoggedIn && username !== auth.user.username"
          class="ms-2 btn btn-sm"
          :class="['btn-outline-' + auth.getUserColor ]"
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
        </a>
      </div>
      <div class="col-6 d-flex justify-content-end">
        <span
          class="me-2"
          :title="basketTotalTitle"
        >{{ basketTotal }} Ft</span>
        <a
          v-if="collapsable"
          class="link-underline link-underline-opacity-0"
          :class="['text-' + auth.getUserColor ]"
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
      </div>
    </div>
    <div
      :id="collapsable ? userId : false"
      :class="{ show: !collapsable || !startCollapsed, collapse: startCollapsed}"
    >
      <div class="row list-group">
        <div
          v-for="item in userBasket"
          :key="item.item_id"
          class="list-group-item d-flex  justify-content-between"
        >
          <div class="col-2">
            <span
              class="badge rounded-pill border"
              :class="[
                'bg-' + auth.getUserColor,
                'border-' + auth.getUserColor + '-subtle']"
            >
              {{ item.quantity }} x
            </span>
          </div>
          <div class="col-8">
            <span>{{ item.item_name }} ({{ item.size_name }})</span>
          </div>
          <div class="col-2 d-flex justify-content-end">
            <span class="text-nowrap pe-0">{{ item.price }} Ft</span>
          </div>
        </div>
      </div>
    </div>
  </div>
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
