<template>
  <div
    v-if="!isLoading"
    class="card"
  >
    <div class="card-header d-flex justify-content-center">
      <div class="col-12 row px-0">
        <div class="col-12 d-flex justify-content-center col-sm-6 col-md-4 justify-content-md-start">
          <h2 class="">
            Heti összegző
          </h2>
        </div>
        <div class="col-12 d-flex justify-content-center col-sm-6 d-md-inline col-md-4">
          <span class="text-center text-nowrap px-2 fs-4">
            {{ getCurrentMonthName }} {{ currentDateSelected.getWeek() }}. hét
          </span>
        </div>
        <div class="col-12 d-flex col-md-4">
          <div class="col-4 d-flex align-items-center justify-content-center">
            <a
              type="button"
              name="button"
              class="btn btn-link text-primary py-0 px-2 "
              title="Ugrás a előző hétre"
              @click="prevWeek()"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="32"
                height="32"
                fill="currentColor"
                class="bi bi-caret-left"
                viewBox="0 0 16 16"
              >
                <path d="M10 12.796V3.204L4.519 8zm-.659.753-5.48-4.796a1 1 0 0 1 0-1.506l5.48-4.796A1 1 0 0 1 11 3.204v9.592a1 1 0 0 1-1.659.753" />
              </svg>
            </a>
          </div>
          <div class="col-4 d-flex align-items-center justify-content-center">
            <v-btn
              v-if="new Date().getDate() !== currentDateSelected.getDate()"
              type="button"
              name="button"
              varian="text"
              class="text-primary bg-secondary py-0 px-2"
              border="primary thin"
              title="Ugrás vissza a mai napra"
              @click="setDay(new Date())"
            >
              Ma
            </v-btn>
          </div>
          <div class="col-4 d-flex align-items-center justify-content-center">
            <a
              type="button"
              name="button"
              class="btn btn-link text-primary py-0 px-2"
              title="Ugrás az következő hétre"
              @click="nextWeek()"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="32"
                height="32"
                fill="currentColor"
                class="bi bi-caret-right"
                viewBox="0 0 16 16"
              >
                <path d="M6 12.796V3.204L11.481 8zm.659.753 5.48-4.796a1 1 0 0 0 0-1.506L6.66 2.451C6.011 1.885 5 2.345 5 3.204v9.592a1 1 0 0 0 1.659.753" />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </div>
    <div class="card-body">
      <div class="">
        <div
          class="col mb-2"
        >
          <div class="col-12 d-md-flex justify-content-md-between">
            <div
              v-for="day in weekdates"
              :key="day"
              style="min-height: 200px"
              class="col border border-2 rounded mx-1 px-2"
              :class="[
                {'border-3': new Date(day).getDate() === currentDateSelected.getDate()},
                new Date(day).getDate() === currentDateSelected.getDate() ? 'border-'+auth.getUserColor : 'border-'+auth.getUserColor + '-subtle'
              ]"
              @click="setDay(day)"
            >
              <div class="row">
                <div class="col-8">
                  <span
                    class="fs-5"
                    :class="[onSameDay(day, new Date()) ? `text-primary` : '']"
                  >
                    {{ new Date(day).toLocaleDateString('hu-HU', {day:'numeric'}) }}.
                    {{ new Date(day).toLocaleDateString('hu-HU', {weekday:'short'}) }}
                  </span>
                </div>
                <div
                  v-if="isThereOrder(history[day])"
                  class="col-4 d-flex justify-content-end"
                >
                  <span title="Ezen a napon te is rendeltél.">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="24"
                      height="24"
                      fill="currentColor"
                      class="bi bi-basket3-fill"
                      viewBox="0 0 16 16"
                    >
                      <path d="M5.757 1.071a.5.5 0 0 1 .172.686L3.383 6h9.234L10.07 1.757a.5.5 0 1 1 .858-.514L13.783 6H15.5a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5H.5a.5.5 0 0 1-.5-.5v-1A.5.5 0 0 1 .5 6h1.717L5.07 1.243a.5.5 0 0 1 .686-.172zM2.468 15.426.943 9h14.114l-1.525 6.426a.75.75 0 0 1-.729.574H3.197a.75.75 0 0 1-.73-.574z" />
                    </svg>
                  </span>
                </div>
              </div>
              <div
                v-if="history[day] !== undefined"
                class="btn btn-link m-0 p-0"
              >
                <button
                  v-for="(order) in Object.values(history[day])"
                  :key="order.id"
                  class="btn btn-link px-0"
                  type="button"
                  name="button"
                  @click="openHistoryPopup(order.id)"
                >
                  <span

                    class=" badge rounder-pill p-2 py-1 fs-6 bg-primary"
                    :title="order.vendor + ' rendelés lett leadva ezen a napon'"
                  >
                    @{{ order.vendor }}
                    <span
                      v-if="order.ordered"
                      :title="'Te is rendeltél ' + order.vendor + '-ból/ből'"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="14"
                        height="14"
                        fill="currentColor"
                        class="bi bi-basket3-fill mb-1"
                        viewBox="0 0 16 16"
                      >
                        <path d="M5.757 1.071a.5.5 0 0 1 .172.686L3.383 6h9.234L10.07 1.757a.5.5 0 1 1 .858-.514L13.783 6H15.5a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5H.5a.5.5 0 0 1-.5-.5v-1A.5.5 0 0 1 .5 6h1.717L5.07 1.243a.5.5 0 0 1 .686-.172zM2.468 15.426.943 9h14.114l-1.525 6.426a.75.75 0 0 1-.729.574H3.197a.75.75 0 0 1-.73-.574z" />
                      </svg>
                    </span>
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="row d-flex align-items-strech">
          <div class="col text-center align-center">
            <span class="btn pe-none border border-secondary-subtle rounded">
              A hét rendeléseinek összege {{ sum }} Ft
            </span>
          </div>
          <div class="col text-center">
            <span class="btn pe-none border border-secondary-subtle rounded">
              {{ orderCount }} db rendelés a héten
            </span>
          </div>
          <Popup
            v-if="showOrderSummary"
            :show-modal="showOrderSummary"
            title="Rendelés összesítő"
            :large="true"
            confirm-text="Ok"
            @cancel="showOrderSummary = false"
            @confirm="showOrderSummary = false"
          >
            <div class="row d-flex align-items-strech">
              <div class="col text-center align-center">
                <span class="btn pe-none border border-secondary-subtle rounded">
                  Összesen {{ calculateHistorySum() }} Ft
                </span>
              </div>
              <div class="col text-center">
                <span class="btn pe-none border border-secondary-subtle rounded">
                  {{ Math.ceil(loaded_menu.order_fee/Object.keys(loaded_menu.basket).length) }} Ft szállítás díj/fő
                </span>
              </div>
            </div>
            <div
              v-for="(user_entry) in loaded_menu.basket"
              :key="user_entry.user_id"
              class="row mt-1 mb-1"
            >
              <div class="list-group-item row m-0">
                <GlobalBasketUser
                  :username="user_entry.username"
                  :user-id="user_entry.user_id"
                  :user-basket="user_entry.items"
                  :order-fee="loaded_menu.order_fee/Object.keys(loaded_menu.basket).length"
                  :start-collapsed="true"
                  :collapsable="true"
                  :copyable="false"
                />
              </div>
            </div>
          </Popup>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineAsyncComponent } from 'vue'
const GlobalBasketUser = defineAsyncComponent(() => import("@/components/GlobalBasketUser.vue"));
const Popup = defineAsyncComponent(() => import("./Popup.vue"));
import { useAuth } from "@/stores/auth";
import { useOrderStore } from "@/stores/order";
import { useVendorStore } from "@/stores/vendor";
import { ref, watch } from "vue";

export default {
  name: "WeekSummary",
  components: {
    Popup,
    GlobalBasketUser,
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
    getCurrentMonthName() {
      return this.currentDateSelected.toLocaleDateString("hu-HU", {month:"long"});
    },
    getTodayDayName() {
      return this.currentDateSelected.toLocaleDateString("hu-HU", {weekday:"long"});
    },
    getTodayDayDate() {
      return this.currentDateSelected.toLocaleDateString("hu-HU");
    },
    orderCount(){
      let sum = 0;
      for (const date in this.history) {
        sum += Object.keys(this.history[date]).length;
      }
      return sum;
    }
  },
  mounted() {
    this.getCurrentWeekDates(new Date()).then(res => {
      this.weekdates = res;
      this.getHistroy(this.weekdates[0], this.weekdates[this.weekdates.length-1]);

      // This might not render if the user is authenticate before thsi line but was not authenticated when the first getHistroy() ran.
      if (!this.auth.isLoggedIn) {
        watch(
          () => this.auth.user,
          () => {
            this.getHistroy(this.weekdates[0], this.weekdates[this.weekdates.length-1]);
          },
          { once: true }
        )
      }
    });
  },
  methods: {
    onSameDay: function(input_date1, input_date2) {
      const date1 = new Date(input_date1);
      const date2 = new Date(input_date2);
      return (
        date1.getFullYear() === date2.getFullYear() &&
        date1.getMonth() === date2.getMonth() &&
        date1.getDate() === date2.getDate()
      );
    },
    isThereOrder: function (orders) {
      if (orders === undefined || !this.auth.isLoggedIn) {
        return false
      }
      for(const order of Object.values(orders)) {
        if("ordered" in order){
            return true;
        }
      }
      return false;
    },
    openHistoryPopup: function(item){
      this.orderStore.fetch(item)
        .then(response => {
            if (response.status === 200) {
              this.loaded_menu = response.data.data;
              this.showOrderSummary = true;
              this.vendorStore.vendors.forEach((vendor) => {
                if (vendor.id === this.loaded_menu.vendor_id ) {
                  this.vendorStore.selectedVendor = vendor;
                }
              });
            }
        })
    },
    async getCurrentWeekDates(date) {
      const weekDates = [];
      const weekStart = new Date(date);
      weekStart.setDate(weekStart.getDate() - weekStart.getAdjustedDay())
      weekStart.setHours(12, 0, 0, 0);
      for (let i = 0; i <= 6; i++) {
        const iterDate = new Date(weekStart);
        iterDate.setDate(weekStart.getDate()+ i)
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
          this.isLoading = false;
          this.calculateStats();
        })
    },
    calculateStats: function() {
      this.sum = 0;
      Object.values(this.history).forEach((date) => {
        Object.values(date).forEach((order) => {
          this.sum+= order.sum;
        })
      })
    },
    calculateHistorySum: function(){
      let sum=0;
      Object.values(this.loaded_menu.basket).forEach((person) => {
        Object.values(person.items).forEach((entry) => {
          sum+= Number(entry.quantity) * Number(entry.price);
        })
      })
      sum += this.loaded_menu.order_fee
      return sum;
    },
    setDay: function(day) {
      const newDate = new Date(day);

      this.weekdates.value = this.getCurrentWeekDates(newDate).then(res => {
        this.weekdates = res;
        this.getHistroy(this.weekdates[0], this.weekdates[this.weekdates.length-1])
      });

      this.currentDateSelected = newDate;
    },
    nextWeek: function() {
      let nextWeek = this.currentDateSelected
      nextWeek.setDate(nextWeek.getDate() + 7)
      this.setDay(nextWeek)
    },
    prevWeek: function() {
      let nextWeek = this.currentDateSelected
      nextWeek.setDate(nextWeek.getDate() - 7)
      this.setDay(nextWeek)
    },
  }
}
</script>

<style>

</style>
