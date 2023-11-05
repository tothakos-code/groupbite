<template>
  <div class="col row my-auto flex-fill">
    <div class="row d-flex justify-content-between">
      <div class="col-6 text-center p-0 d-flex">
        <div class="row justify-content-center px-1">
          <span class="text-center text-nowrap px-2">
            {{ getCurrentMonthName }}
          </span>
        </div>
      </div>
      <div class="col-6 p-0 d-flex justify-content-end">
        <button
          v-if="new Date().getDate() !== this.currentDateSelected.getDate()"
          type="button"
          name="button"
          @click="this.setDay(new Date())"
          class="btn btn-sm py-0"
          :class="['btn-' + auth.userColor.value ]"
        >
          <span>Ma</span>
        </button>
      </div>
    </div>
    <div
      class="row col"
      v-for="item in weekdates.value"
      :key="item"
      @click="setDay(item)"
    >
      <div class="col">
        <div class="row">
          <span
            :class="[onSameDay(item, new Date()) ? 'text-'+this.auth.matchUiColorWithBuiltIn.value : '']"

          >
            {{ new Date(item).toLocaleDateString('hu-HU', {weekday:'short'}) }}
          </span>
        </div>
        <div
          class="row border border-2"
          :class="[
            {'border-3': new Date(item).getDate() === this.currentDateSelected.getDate()},
            new Date(item).getDate() === this.currentDateSelected.getDate() ? 'border-'+this.auth.matchUiColorWithBuiltIn.value : 'border-'+this.auth.matchUiColorWithBuiltIn.value + '-subtle'
          ]"
        >
          <span
            class="col p-1 pe-0 aling-items-center"
            :class="[onSameDay(item, new Date()) ? 'text-'+this.auth.matchUiColorWithBuiltIn.value : '']"

          >
            {{ new Date(item).toLocaleDateString('hu-HU', {day:'numeric'}) }}
          </span>
          <span
            class="col p-1 ps-0"
            v-if="item in user_states && JSON.stringify(user_states[item]) !== JSON.stringify({})"
            >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-basket3-fill" viewBox="0 0 16 16">
              <path d="M5.757 1.071a.5.5 0 0 1 .172.686L3.383 6h9.234L10.07 1.757a.5.5 0 1 1 .858-.514L13.783 6H15.5a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5H.5a.5.5 0 0 1-.5-.5v-1A.5.5 0 0 1 .5 6h1.717L5.07 1.243a.5.5 0 0 1 .686-.172zM2.468 15.426.943 9h14.114l-1.525 6.426a.75.75 0 0 1-.729.574H3.197a.75.75 0 0 1-.73-.574z"/>
            </svg>
          </span>
        </div>
        <div class="row" :class="{'border-3':new Date(item).getDate() === this.currentDateSelected.getDate()}">
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import { ref, watchEffect } from 'vue';
import { state } from '@/socket';
import { useAuth } from '@/auth';

export default {
  name: 'DateStamp',
  data() {
    return {
      currentDateSelected: new Date()
    }
  },
  mounted() {
    this.weekdates.value = this.getCurrentWeekDates(new Date());
    const currentDate = new Date();
    const currentDayOfWeek = currentDate.getDay();
    const startDate = new Date(currentDate);
    startDate.setDate(currentDate.getDate() - currentDayOfWeek + (currentDayOfWeek === 0 ? -6 : 1));
    const endDate = new Date();
    endDate.setDate(startDate.getDate() + 6);
    this.getUserBasketStates(startDate.toISOString().split('T')[0], endDate.toISOString().split('T')[0])
  },
  setup() {
    const user_states = ref({});
    const weekdates = ref([]);
    const auth = useAuth();
    watchEffect(() => {
      console.log(state.localBasket);
      user_states.value[state.selectedDate.toISOString().split('T')[0]] = state.localBasket
    })
    return {
      user_states,
      weekdates,
      auth
    }
  },
  props: {
    'limitToCurrentWeek': Boolean,
    'dateRange': Number
  },
  emits: ['selectedDate'],
  computed: {
    getTodayDayName() {
      return this.currentDateSelected.toLocaleDateString('hu-HU', {weekday:'long'});
    },
    getTodayDayDate() {
      return this.currentDateSelected.toLocaleDateString('hu-HU');
    },
    getCurrentMonthName() {
      return this.currentDateSelected.toLocaleDateString('hu-HU', {month:'long'});
    }
  },
  methods: {
    getCurrentWeekDates(date) {
      const centerDate = new Date(date);
      centerDate.setHours(12, 0, 0, 0);
      console.log("centerDate: " + centerDate.toISOString().split('T')[0]);

      const weekDates = [];

      for (let i = -this.dateRange; i <= this.dateRange; i++) {
        const iterDate = new Date(centerDate);
        iterDate.setDate(centerDate.getDate() + i);

        const formattedDate = iterDate.toISOString().split('T')[0];
        weekDates.push(formattedDate);
      }
      console.log(weekDates);
      return weekDates;
    },
    getUserBasketStates: function(day_from, day_to) {
      if (state.user.username === undefined) {
        return;
      }
      fetch(`http://${window.location.host}/api/order/get-user-basket-between`,{
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          "user": state.user.username,
          'date_from': day_from,
          'date_to': day_to
        })
      })
        .then(response => response.json())
          .then(data => {
            console.log(data);
            this.user_states = data
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
    setDay: function(day) {
      const newDate = new Date(day);
      this.weekdates.value = this.getCurrentWeekDates(newDate)
      this.currentDateSelected = newDate;
      this.$emit('selectedDate', this.currentDateSelected);
    }
  }
}
</script>

<style>
</style>
