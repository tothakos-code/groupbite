<template>
  <div class="card">
    <div class="card-header">
      <div class="col-3 col-md-6 col-lg-8 row px-0">
        <div class="col-0 d-none col-lg-8 d-lg-inline my-auto truncate ms-0">
          <h2 class="">
            Heti összegző
          </h2>
        </div>
        <div class="row row-2 justify-content-between">
          <div class="col-6 d-flex p-0 ">
            <div class="row justify-content-center px-1">
              <span class="text-center text-nowrap px-2">
                {{ getCurrentMonthName }} {{ currentDateSelected.getWeek() }}. hét
              </span>
            </div>
          </div>
          <div class="col-6 p-0 d-flex justify-content-end">
            <button
              v-if="new Date().getDate() !== currentDateSelected.getDate()"
              type="button"
              name="button"
              class="btn btn-sm py-0"
              :class="['btn-' + auth.userColor.value ]"
              @click="setDay(new Date())"
            >
              <span>Ma</span>
            </button>
          </div>
        </div>
      </div>
      <div class="col-9 col-md-6 col-lg-4 d-flex flex-fill px-0" />
    </div>
    <div class="card-body">
      <div class="">
        <div
          class="col mb-2"
        >
          <div class="row row-10 d-flex justify-content-between">
            <div
              v-for="day in weekdates"
              :key="day"
              style="min-height: 200px"
              class="col border border-2 rounded mx-1 px-2"
              :class="[
                {'border-3': new Date(day).getDate() === currentDateSelected.getDate()},
                new Date(day).getDate() === currentDateSelected.getDate() ? 'border-'+auth.matchUiColorWithBuiltIn.value : 'border-'+auth.matchUiColorWithBuiltIn.value + '-subtle'
              ]"
              @click="setDay(day)"
            >
              <div class="row">
                <div class="col-8">
                  <span
                    class="fs-5"
                    :class="[onSameDay(day, new Date()) ? 'text-'+auth.matchUiColorWithBuiltIn.value : '']"
                  >
                    {{ new Date(day).toLocaleDateString('hu-HU', {day:'numeric'}) }}.
                    {{ new Date(day).toLocaleDateString('hu-HU', {weekday:'short'}) }}
                  </span>
                </div>
                <div
                  v-if="isThereOrder(day)"
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
                  v-for="v,k in history[day]"
                  :key="k"
                  class="btn btn-link"
                  type="button"
                  name="button"
                  @click="openHistoryPopup(v.id)"
                >
                  <span

                    class=" badge rounder-pill bg-falusi p-2 py-1 fs-6"
                    :title="v.vendor + ' rendelés lett leadva ezen a napon'"
                  >
                    @{{ v.vendor }}
                  </span>
                </button>
              </div>
            </div>
            <div
              class="row"
              :class="{'border-3':new Date(day).getDate() === currentDateSelected.getDate()}"
            />
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
            {{ boxCount }} db doboz
          </span>
        </div>
        <div class="col text-center">
          <span class="btn pe-none border border-secondary-subtle rounded">
            {{ transportFeePerPerson }} Ft szállítás díj/fő
          </span>
        </div>

        <Popup
          :show-modal="showOrderSummary"
          title="Rendelés összesítő"
          @cancel="showOrderSummary = false"
        >
          <div class="row d-flex align-items-strech">
            <div class="col text-center align-center">
              <span class="btn pe-none border border-secondary-subtle rounded">
                Összesen {{ calculateHistorySum() }} Ft
              </span>
            </div>
            <div class="col text-center">
              <span class="btn pe-none border border-secondary-subtle rounded">
                {{ boxCount }} db doboz
              </span>
            </div>
            <div class="col text-center">
              <span class="btn pe-none border border-secondary-subtle rounded">
                {{ transportFeePerPerson }} Ft szállítás díj/fő
              </span>
            </div>
          </div>
          <div
            v-for="(user_entry) in loaded_menu"
            :key="user_entry.id"
            class="row mt-1 mb-1"
          >
            <div class="list-group-item row m-0">
              <GlobalBasketPerson
                :name="user_entry.username"
                :person-basket="user_entry.basket_entry"
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
</template>

<script>
import GlobalBasketPerson from './GlobalBasketPerson.vue'
import Popup from './Popup.vue';
import { useAuth } from '@/auth';
import { transportFeePerPerson, personCount, basketSum, boxCount } from '@/basket';
import axios from 'axios';
import { state } from '@/socket';
import { ref, watch } from 'vue';

export default {
  name: 'WeekSummary',
  components: {
    Popup,
    GlobalBasketPerson,
  },
  emits: ['close'],
  setup() {
    const user_states = ref({});
    const weekdates = ref([]);
    const auth = useAuth();
    return {
      auth,
      transportFeePerPerson,
      user_states,
      weekdates,
      personCount,
      basketSum,
      boxCount
    }
  },
  data() {
    return {
      history: {},
      selected_history: new Date(),
      currentDateSelected: new Date(),
      showOrderSummary: false,
      loaded_menu: {},
      sum: 0,
      user_avg: 0,
      user_avg_p_day: 0,
    }
  },
  computed: {
    getCurrentMonthName() {
      return this.currentDateSelected.toLocaleDateString('hu-HU', {month:'long'});
    },
    getTodayDayName() {
      return this.currentDateSelected.toLocaleDateString('hu-HU', {weekday:'long'});
    },
    getTodayDayDate() {
      return this.currentDateSelected.toLocaleDateString('hu-HU');
    },
  },
  mounted() {
    this.getHistroy();
    this.getCurrentWeekDates(new Date()).then(res => {
      this.weekdates = res;
      if (this.auth.isLoggedIn) {
        this.getUserBasketStates(this.weekdates[0], this.weekdates[this.weekdates.length -1 ])
      } else {
        watch(
          () => state.user,
          () => {
            this.getUserBasketStates(this.weekdates[0], this.weekdates[this.weekdates.length -1 ])
          },
          { once: true }
        )
      }
    });
  },
  methods: {
    getUserBasketStates: function(day_from, day_to) {
      if (state.user === undefined) {
        return;
      }
      axios.post(
        `http://${window.location.host}/api/order/get-user-basket-between`,
        {
          "user": state.user.username,
          "user_id": state.user.id,
          'date_from': day_from,
          'date_to': day_to
        }
      )
        .then(response => {
          this.user_states = response.data
        })
        .catch(error => console.error(error));
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
    isThereOrder: function (date) {
      for(var i in this.user_states){
          if(this.user_states[i].date == date){
              return true;
          }
      }
      return false;
    },
    openHistoryPopup: function(item){
      axios.get(`http://${window.location.host}/api/order/${item}/get-basket`)
        .then(response => {
            this.loaded_menu = response.data;
            for (const [index, user] of Object.entries(this.loaded_menu)){
              console.log("item");
              console.log(index);
              console.log(user);
            }
            this.showOrderSummary = true
        })
    },
    async getCurrentWeekDates(date) {
      const weekDates = [];
      const weekStart = new Date(date);
      weekStart.setDate(weekStart.getDate() - weekStart.getDay())
      weekStart.setHours(12, 0, 0, 0);
      for (let i = 0; i <= 6; i++) {
        const iterDate = new Date(weekStart);
        iterDate.setDate(weekStart.getDate()+ i+1)
        const formattedDate = iterDate.toISODate();
        weekDates.push(formattedDate);
      }
      return weekDates;
    },
    getHistroy: function() {
      let url = `http://${window.location.host}/api/order/history`
      axios.post(url, {
          'date_from': '2024-05-27',
          'date_to': '2024-05-31',
        })
        .then((data) => {
          this.history = data.data;
          this.calculateStats();
        })
        .catch(e => {
          console.log(e);
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
      Object.values(this.loaded_menu).forEach((person) => {
        Object.values(person.basket_entry).forEach((entry) => {
          sum+= Number(entry.count) * Number(entry.item.price);
        })
      })
      return sum;
    },
    setDay: function(day) {
      const newDate = new Date(day);
      this.weekdates.value = this.getCurrentWeekDates(newDate)
      this.currentDateSelected = newDate;
      this.getHistroy(this.currentDateSelected)
    }
  }
}
</script>

<style>

</style>
