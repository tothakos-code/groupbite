<template>
  <v-card
    class="border-sm fill-height"
  >
    <v-card-title class="bg-header border-b-sm  d-flex justify-content-center">
      <v-row
        class="px-0 d-flex"
        no-gutters
        justify="start"
      >
        <v-col
          align-self="center"
        >
          <h2 class="">
            Fizetéselosztó
          </h2>
        </v-col>
      </v-row>
    </v-card-title>
    <v-card-text class="">
      <v-list two-line>
        <v-list-item
          v-for="(user, userId) in calculateUsersSum"
          :key="userId"
        >
          <v-list-item-title>{{ user.username }}</v-list-item-title>
          <v-list-item-subtitle>
            Teljes összeg: {{ user.totalSpent }} Ft
          </v-list-item-subtitle>
        </v-list-item>
      </v-list>
      <div
        v-if="orderCount === 0"
        class="mb-2"
      >
        <span class="text-body-1">
          Válassz ki egy vagy több rendelést az elosztáshoz
        </span>
      </div>
      <v-row
        class="mt-auto"
      >
        <v-col class="d-flex align-items-strech align-end">
          <div class="col text-center align-center">
            <span class="text-nowrap btn pe-none border border-secondary-subtle rounded">
              Összesen {{ calculateOrdersSum }} Ft
            </span>
          </div>
          <div class="col text-center align-center">
            <span class="text-nowrap btn pe-none border border-secondary-subtle rounded">
              Kijelölt rendelés {{ orderCount }} db
            </span>
          </div>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
import { useAuth } from "@/stores/auth";
import { useOrderStore } from "@/stores/order";
import { useVendorStore } from "@/stores/vendor";

export default {
  name: "OrderSplitter",
  components: {
  },
  emits: ["close"],
  setup() {
    const auth = useAuth();
    const orderStore = useOrderStore();
    const vendorStore = useVendorStore();
    return {
      auth,
      orderStore,
      vendorStore,
    }
  },
  data() {
    return {
      history: {},
      selected_history: new Date(),
      currentDateSelected: new Date(),
      showOrderSummary: false,
      loaded_menu: { basket:{}},
      sum: 0,
      user_avg: 0,
      user_avg_p_day: 0,
      isLoading: true
    }
  },
  computed: {
    calculateOrdersSum() {
      let sum=0;
      Object.values(this.orderStore.selectedOrders).forEach((order) => {
        Object.values(order.basket).forEach((person) => {
          Object.values(person.items).forEach((entry) => {
            sum+= Number(entry.quantity) * Number(entry.price);
          })
        })
        sum+=order.order_fee
      });

      return sum;
    },
    calculateUsersSum() {
      const summary = {};

      this.orderStore.selectedOrders.forEach(order => {
          const userCount = Object.keys(order.basket).length;

          const orderFeeperuser = Math.ceil(order.order_fee/userCount)
          Object.values(order.basket).forEach(userBasket => {
              const { user_id, username, items } = userBasket;

              if (!summary[user_id]) {
                  summary[user_id] = {
                      username,
                      totalSpent: 0,
                  };
              }

              let orderTotal = 0;

              items.forEach(item => {
                  orderTotal += item.price * item.quantity;
              });
              orderTotal += orderFeeperuser;

              summary[user_id].totalSpent += orderTotal;
          });
      });

      return summary;
    },
    orderCount(){
      return this.orderStore.selectedOrders.length;
    }
  },
  mounted() {

  },
  methods: {
    resetOrders() {
      this.orderStore.selectedOrders = []
    },

    // calculateOrdersSum: function(){
    //   let sum=0;
    //   Object.values(this.orderStore.selectedOrders).forEach((order) => {
    //     Object.values(order.basket).forEach((person) => {
    //       Object.values(person.items).forEach((entry) => {
    //         sum+= Number(entry.quantity) * Number(entry.price);
    //       })
    //     })
    //     sum+=order.order_fee
    //   });
    //
    //   sum += this.loaded_menu.order_fee
    //   return sum;
    // },

  }
}
</script>

<style>

</style>
