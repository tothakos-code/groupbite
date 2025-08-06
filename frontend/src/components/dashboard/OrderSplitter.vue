<template>
  <v-container
    fluid
    class=""
  >
    <!-- Loading State -->
    <v-skeleton-loader
      v-if="isLoading"
      type="card"
      class="mx-auto"
      max-width="1000"
    />
    <v-card
      v-else
      elevation="2"
      class="fill-height d-flex flex-column"
    >
      <!-- Header -->
      <v-card-title class="bg-primary text-white pa-3">
        <div class="d-flex align-center">
          <h2 class="text-h5 font-weight-bold">
            <v-icon class="me-2">
              mdi-account-multiple
            </v-icon>
            Fizetéselosztó
          </h2>
        </div>
      </v-card-title>

      <!-- Content -->
      <v-card-text class="flex-grow-1 d-flex flex-column pa-4">
        <!-- Users List -->
        <div class="flex-grow-1">
          <v-fade-transition>
            <v-list
              v-if="orderCount > 0"
              class="pa-0"
            >
              <v-list-item
                v-for="(user, userId) in calculateUsersSum"
                :key="userId"
                class="px-0 mb-2"
              >
                <p class="text-h6 font-weight-medium">
                  {{ user.username }}
                  <v-chip
                    :color="getUserColor(userId)"
                    variant="tonal"
                    size="small"
                    class="font-weight-bold"
                  >
                    {{ formatCurrency(user.totalSpent) }}
                  </v-chip>
                </p>
              </v-list-item>
            </v-list>
          </v-fade-transition>

          <!-- Empty State -->
          <v-fade-transition>
            <div
              v-if="orderCount === 0"
              class="text-center py-8"
            >
              <v-icon
                size="64"
                color="grey-lighten-2"
                class="mb-4"
              >
                mdi-calculator-variant
              </v-icon>
              <div class="text-h6 text-grey-darken-1 mb-2">
                Nincs kijelölt rendelés
              </div>
              <div class="text-body-1 text-grey-lighten-1">
                Válassz ki egy vagy több rendelést az elosztáshoz
              </div>
            </div>
          </v-fade-transition>
        </div>

        <!-- Summary Section -->
        <div class="mt-4">
          <v-divider class="mb-4" />
          <v-fade-transition>
            <div
              v-if="orderStore.selectedOrders.length > 0"
              class=""
            >
              <v-icon class="me-2">
                mdi-basket
              </v-icon>
              <span class="text-h6">Kiválasztott rendelések</span>
              <v-list density="compact">
                <v-list-item
                  v-for="order in orderStore.selectedOrders"
                  :key="order.id"
                >
                  <template #prepend>
                    <v-icon
                      color="success"
                      size="small"
                    >
                      mdi-check-circle
                    </v-icon>
                  </template>

                  <v-list-item-title class="text-body-2">
                    @{{ order.vendor }}
                  </v-list-item-title>

                  <v-list-item-subtitle>
                    {{ formatCurrency(order.total_price + order.order_fee) }}
                  </v-list-item-subtitle>

                  <template #append>
                    <v-btn
                      icon
                      variant="text"
                      size="x-small"
                      @click="removeFromCalculation(order.id)"
                    >
                      <v-icon size="small">
                        mdi-close
                      </v-icon>
                    </v-btn>
                  </template>
                </v-list-item>
              </v-list>
            </div>
          </v-fade-transition>
          <v-row>
            <v-col
              cols="12"
              md="6"
            >
              <v-card
                variant="outlined"
                class="text-center pa-3"
                :class="orderCount > 0 ? 'border-success' : 'border-grey-lighten-2'"
              >
                <v-card-title class="pb-2 text-body-2">
                  <v-icon
                    class="me-2"
                    :color="orderCount > 0 ? 'success' : 'grey-lighten-1'"
                  >
                    mdi-cash-multiple
                  </v-icon>
                  Teljes összeg
                </v-card-title>
                <v-card-text class="pa-0">
                  <div
                    class="font-weight-bold"
                    :class="orderCount > 0 ? 'text-success' : 'text-grey-lighten-1'"
                  >
                    {{ formatCurrency(calculateOrdersSum) }}
                  </div>
                </v-card-text>
              </v-card>
            </v-col>

            <v-col
              cols="12"
              md="6"
            >
              <v-card
                variant="outlined"
                class="text-center pa-3"
                :class="orderCount > 0 ? 'border-primary' : 'border-grey-lighten-2'"
              >
                <v-card-title class="pb-2 text-body-2">
                  <v-icon
                    class="me-2"
                    :color="orderCount > 0 ? 'primary' : 'grey-lighten-1'"
                  >
                    mdi-receipt
                  </v-icon>
                  Rendelések
                </v-card-title>
                <v-card-text class="pa-0">
                  <div
                    class="font-weight-bold"
                    :class="orderCount > 0 ? 'text-primary' : 'text-grey-lighten-1'"
                  >
                    {{ orderCount }} db
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <!-- Action Buttons -->
          <v-row
            v-if="orderCount > 0"
            class="mt-4"
          >
            <v-col
              cols="12"
            >
              <v-btn
                block
                variant="outlined"
                color="error"
                prepend-icon="mdi-delete"
                @click="resetOrders"
              >
                Kijelölések törlése
              </v-btn>
            </v-col>
          </v-row>
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import { useAuth } from "@/stores/auth";
import { useOrderStore } from "@/stores/order";
import { useVendorStore } from "@/stores/vendor";

export default {
  name: "OrderSplitter",
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
      userColors: [
        'primary', 'secondary', 'success', 'warning', 'error', 'info',
        'purple', 'pink', 'indigo', 'cyan', 'teal', 'green'
      ]
    }
  },
  computed: {
    calculateOrdersSum() {
      let sum = 0;
      this.orderStore.selectedOrders.forEach((order) => {
        Object.values(order.basket).forEach((person) => {
          Object.values(person.items).forEach((entry) => {
            sum += Number(entry.quantity) * Number(entry.price);
          });
        });
        sum += order.order_fee;
      });
      return sum;
    },
    calculateUsersSum() {
      const summary = {};
      this.orderStore.selectedOrders.forEach(order => {
        const userCount = Object.keys(order.basket).length;
        const orderFeePerUser = Math.ceil(order.order_fee / userCount);

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
          orderTotal += orderFeePerUser;
          summary[user_id].totalSpent += orderTotal;
        });
      });
      return summary;
    },
    orderCount() {
      return this.orderStore.selectedOrders.length;
    }
  },
  methods: {
    formatCurrency(amount) {
      return new Intl.NumberFormat('hu-HU', {
        style: 'currency',
        currency: 'HUF',
        minimumFractionDigits: 0
      }).format(amount);
    },
    getUserColor(userId) {
      // Generate consistent color for each user based on their ID
      const hash = userId.toString().split('').reduce((a, b) => {
        a = ((a << 5) - a) + b.charCodeAt(0);
        return a & a;
      }, 0);
      return this.userColors[Math.abs(hash) % this.userColors.length];
    },
    removeFromCalculation(orderId) {
      this.orderStore.selectedOrders = this.orderStore.selectedOrders.filter(order => order.id !== orderId);
    },
    resetOrders() {
      this.orderStore.selectedOrders = [];
    },
  }
}
</script>

<style scoped>
.v-list-item {
  border-radius: 8px;
  margin-bottom: 8px;
  transition: all 0.2s ease;
}

.v-list-item:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

.v-card {
  border-radius: 12px !important;
}

.border-success {
  border-color: rgb(var(--v-theme-success)) !important;
  border-width: 2px !important;
}

.border-primary {
  border-color: rgb(var(--v-theme-primary)) !important;
  border-width: 2px !important;
}

.border-grey-lighten-2 {
  border-color: rgb(var(--v-theme-grey-lighten-2)) !important;
}
</style>
