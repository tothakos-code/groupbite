<template>
  <v-container
    fluid
    class=""
  >
    <!-- Loading State -->
    <v-card
      elevation="2"
      class="mb-4"
    >
      <v-card-title class="bg-primary text-white pa-4">
        <v-row
          align="center"
          no-gutters
        >
          <v-col
            cols="12"
            md="4"
            class="text-center text-md-start"
          >
            <h2 class="text-h5 font-weight-bold">
              <v-icon class="me-2">
                mdi-timeline
              </v-icon>
              Rendelés idővonal
            </h2>
          </v-col>

          <v-col
            cols="12"
            md="4"
            class="text-center"
          >
            <v-chip
              color="white"
              text-color="primary"
              size="large"
              class="font-weight-bold"
            >
              {{ getCurrentMonthName }} {{ currentDateSelected.getWeek() }}. hét
            </v-chip>
          </v-col>

          <v-col
            cols="12"
            md="4"
          >
            <v-row
              justify="center"
              justify-md="end"
              no-gutters
              class="align-center"
            >
              <!-- Left arrow button -->
              <v-btn
                icon
                variant="text"
                color="white"
                :disabled="isLoading"
                @click="prevWeek()"
              >
                <v-icon>mdi-chevron-left</v-icon>
              </v-btn>

              <!-- Middle button (always rendered, just hidden if current week) -->
              <div
                style="width: 130px;"
                class="mx-2 text-center"
              >
                <v-btn
                  v-show="!isCurrentWeek"
                  variant="outlined"
                  color="white"
                  size="small"
                  block
                  :disabled="isLoading"
                  @click="goToCurrentWeek()"
                >
                  Aktuális hét
                </v-btn>
              </div>

              <!-- Right arrow button -->
              <v-btn
                icon
                variant="text"
                color="white"
                :disabled="isLoading"
                @click="nextWeek()"
              >
                <v-icon>mdi-chevron-right</v-icon>
              </v-btn>
            </v-row>
          </v-col>
        </v-row>
      </v-card-title>
      <v-skeleton-loader
        v-if="isLoading"
        type="card"
        class="mx-auto"
        max-width="1000"
      />
      <v-card-text
        v-else
        class="pa-4"
      >
        <!-- Date Tabs for Quick Navigation -->
        <v-chip-group
          v-model="selectedDay"
          mandatory
          selected-class="text-primary"
          class="mb-4"
        >
          <v-chip
            v-for="(day, index) in weekdates"
            :key="day"
            :value="index"
            :color="onSameDay(day, new Date()) ? 'secondary' : 'grey-lighten-3'"
            :variant="onSameDay(day, new Date()) ? 'flat' : 'outlined'"
            size="small"
            class="me-2"
          >
            <template
              v-if="hasOrdersOnDay(day)"
              #prepend
            >
              <v-badge
                :content="getOrderCountForDay(day)"
                color="success"
                inline
              />
            </template>
            {{ new Date(day).toLocaleDateString('hu-HU', {weekday:'short', day:'numeric'}) }}
          </v-chip>
        </v-chip-group>

        <!-- Current Day's Orders -->
        <div v-if="getCurrentDayOrders().length > 0">
          <h3 class="text-h6 mb-3 text-grey-darken-2">
            {{ new Date(weekdates[selectedDay]).toLocaleDateString('hu-HU', {weekday:'long', day:'numeric', month:'long'}) }}
          </h3>

          <v-row>
            <v-col
              v-for="order in getCurrentDayOrders()"
              :key="order.id"
              cols="12"
              sm="6"
              md="4"
            >
              <OrderChip
                :order="order"
                :is-selected="isOrderInList(order.id)"
                @click="addToCalculation(order.id)"
              />
            </v-col>
          </v-row>
        </div>

        <!-- Empty State for Selected Day -->
        <div
          v-else
          class="text-center py-8"
        >
          <v-icon
            size="64"
            color="grey-lighten-2"
            class="mb-4"
          >
            mdi-calendar-blank
          </v-icon>
          <h3 class="text-h6 text-grey-lighten-1 mb-2">
            Nincs rendelés ezen a napon
          </h3>
          <p class="text-grey-lighten-1">
            {{ new Date(weekdates[selectedDay]).toLocaleDateString('hu-HU', {weekday:'long', day:'numeric', month:'long'}) }}
          </p>
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import { useAuth } from "@/stores/auth";
import { useOrderStore } from "@/stores/order";
import { useVendorStore } from "@/stores/vendor";
import { ref, watch } from "vue";
import OrderChip from "@/components/dashboard/OrderChip"

export default {
  name: "OrderHomeUI",
  components: {
    OrderChip
  },
  emits: ["close"],
  setup() {
    const user_states = ref({});
    const weekdates = ref([]);
    const auth = useAuth();
    const orderStore = useOrderStore();
    const vendorStore = useVendorStore();

    return {
      auth,
      orderStore,
      vendorStore,
      user_states,
      weekdates
    }
  },
  data() {
    return {
      history: {},
      selectedDay: 0, // Index of currently selected day
      currentDateSelected: new Date(),
      showOrderSummary: false,
      loaded_menu: { basket: {} },
      sum: 0,
      user_avg: 0,
      user_avg_p_day: 0,
      isLoading: true
    }
  },
  computed: {
    getCurrentMonthName() {
      return this.currentDateSelected.toLocaleDateString("hu-HU", { month: "long" });
    },
    orderCount() {
      let sum = 0;
      for (const date in this.history) {
        sum += Object.keys(this.history[date]).length;
      }
      return sum;
    },
    isCurrentWeek() {
      const today = new Date();
      const currentWeekStart = new Date(today);
      currentWeekStart.setDate(today.getDate() - today.getAdjustedDay());

      const selectedWeekStart = new Date(this.currentDateSelected);
      selectedWeekStart.setDate(this.currentDateSelected.getDate() - this.currentDateSelected.getAdjustedDay());

      return currentWeekStart.toDateString() === selectedWeekStart.toDateString();
    },
    selectedOrdersTotal() {
      return this.orderStore.selectedOrders.reduce((total, order) => total + (order.sum || 0), 0);
    }
  },
  mounted() {
    this.getCurrentWeekDates(new Date()).then(res => {
      this.weekdates = res;
      // Set selected day to today if it's in current week
      const todayIndex = res.findIndex(day => this.onSameDay(day, new Date()));
      if (todayIndex !== -1) {
        this.selectedDay = todayIndex;
      }

      this.getHistroy(this.weekdates[0], this.weekdates[this.weekdates.length - 1]);

      if (!this.auth.isLoggedIn) {
        watch(
          () => this.auth.user,
          () => {
            this.getHistroy(this.weekdates[0], this.weekdates[this.weekdates.length - 1]);
          },
          { once: true }
        )
      }
    });
  },
  methods: {
    formatCurrency(amount) {
      return new Intl.NumberFormat('hu-HU', {
        style: 'currency',
        currency: 'HUF',
        minimumFractionDigits: 0
      }).format(amount);
    },
    getVendorColor(vendor) {
      // Generate consistent colors for vendors
      const colors = ['primary', 'secondary', 'accent', 'info', 'warning', 'error'];
      const hash = vendor.split('').reduce((a, b) => a + b.charCodeAt(0), 0);
      return colors[hash % colors.length];
    },
    getOrderStateColor(stateId) {
      switch (stateId) {
        case 'closed': return 'error';
        case 'order': return 'warning';
        default: return 'success';
      }
    },
    getOrderStateIcon(stateId) {
      switch (stateId) {
        case 'closed': return 'mdi-lock';
        case 'order': return 'mdi-clock';
        default: return 'mdi-lock-open';
      }
    },
    getOrderStateText(stateId) {
      switch (stateId) {
        case 'closed': return 'Lezárva';
        case 'order': return 'Folyamatban';
        default: return 'Nyitott';
      }
    },
    getCurrentDayOrders() {
      const selectedDate = this.weekdates[this.selectedDay];
      return Object.values(this.history[selectedDate] || {});
    },
    hasOrdersOnDay(day) {
      return this.history[day] && Object.keys(this.history[day]).length > 0;
    },
    getOrderCountForDay(day) {
      return this.history[day] ? Object.keys(this.history[day]).length : 0;
    },
    getDayTotal(day) {
      if (!this.history[day]) return 0;
      return Object.values(this.history[day]).reduce((total, order) => total + (order.sum || 0), 0);
    },
    goToOrder: function(order) {
      this.$router.push({ path: "/menu/" + order.vendor + "/" + order.date_of_order });
    },
    onSameDay: function(input_date1, input_date2) {
      const date1 = new Date(input_date1);
      const date2 = new Date(input_date2);
      return (
        date1.getFullYear() === date2.getFullYear() &&
        date1.getMonth() === date2.getMonth() &&
        date1.getDate() === date2.getDate()
      );
    },
    isOrderInList(orderId) {
      return this.orderStore.selectedOrders.some(order => order.id === orderId);
    },
    addToCalculation: function(orderId) {
      if (!this.isOrderInList(orderId)) {
        this.orderStore.fetch(orderId)
          .then(response => {
            if (response.status === 200) {
              this.orderStore.selectedOrders.push(response.data.data);
            }
          });
      } else {
        this.orderStore.selectedOrders = this.orderStore.selectedOrders.filter(order => order.id !== orderId);
      }
    },
    async getCurrentWeekDates(date) {
      const weekDates = [];
      const weekStart = new Date(date);
      weekStart.setDate(weekStart.getDate() - weekStart.getAdjustedDay());
      weekStart.setHours(12, 0, 0, 0);

      for (let i = 0; i <= 6; i++) {
        const iterDate = new Date(weekStart);
        iterDate.setDate(weekStart.getDate() + i);
        const formattedDate = iterDate.toISODate();
        weekDates.push(formattedDate);
      }
      return weekDates;
    },
    getHistroy: function(from, to) {
      this.orderStore.fetchHistory({
        "date_from": new Date(from).toISODate(),
        "date_to": new Date(to).toISODate(),
        "user_id": this.auth.isLoggedIn ? this.auth.user.id : undefined
      })
        .then(response => {
          this.history = response.data.data;
          this.calculateStats();
          this.isLoading = false;
        });
    },
    calculateStats: function() {
      this.sum = 0;
      Object.values(this.history).forEach((date) => {
        Object.values(date).forEach((order) => {
          this.sum += order.sum;
        });
      });
    },
    goToCurrentWeek: function() {
      this.setDay(new Date());
    },
    setDay: function(day) {
      const newDate = new Date(day);
      this.currentDateSelected = newDate;
      this.isLoading = true;
      this.getCurrentWeekDates(newDate).then(res => {
        this.weekdates = res;
        // Set selected day to today if switching to current week
        const todayIndex = res.findIndex(date => this.onSameDay(date, new Date()));
        if (todayIndex !== -1) {
          this.selectedDay = todayIndex;
        } else {
          this.selectedDay = 0;
        }
        this.getHistroy(this.weekdates[0], this.weekdates[this.weekdates.length - 1]);
      });
    },
    nextWeek: function() {
      let nextWeek = new Date(this.currentDateSelected);
      nextWeek.setDate(nextWeek.getDate() + 7);
      this.setDay(nextWeek);
    },
    prevWeek: function() {
      let prevWeek = new Date(this.currentDateSelected);
      prevWeek.setDate(prevWeek.getDate() - 7);
      this.setDay(prevWeek);
    }
  }
}
</script>

<style scoped>
.order-card {
  transition: all 0.2s ease;
  border-radius: 12px !important;
}

.order-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}

.v-card {
  border-radius: 12px !important;
}


.cursor-pointer {
  cursor: pointer;
}

.border-success {
  border: 2px solid rgb(var(--v-theme-success)) !important;
}
</style>
