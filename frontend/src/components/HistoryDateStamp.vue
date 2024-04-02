<template>
  <div
    class="col mb-2"
  >
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
    <div class="row row-10 d-flex justify-content-between">
      <div
        v-for="item in weekdates"
        :key="item"
        style="min-height: 150px"
        class="col border border-2 rounded mx-1 px-2"
        :class="[
          {'border-3': new Date(item).getDate() === currentDateSelected.getDate()},
          new Date(item).getDate() === currentDateSelected.getDate() ? 'border-'+auth.matchUiColorWithBuiltIn.value : 'border-'+auth.matchUiColorWithBuiltIn.value + '-subtle'
        ]"
        @click="setDay(item)"
      >
        <div class="row">
          <div class="col-8">
            <span
              class=""
              :class="[onSameDay(item, new Date()) ? 'text-'+auth.matchUiColorWithBuiltIn.value : '']"
            >
              {{ new Date(item).toLocaleDateString('hu-HU', {day:'numeric'}) }}.
              {{ new Date(item).toLocaleDateString('hu-HU', {weekday:'short'}) }}
            </span>
          </div>
          <div
            v-if="isThereOrder(item)"
            class="col-4 d-flex justify-content-end"
          >
            <span title="Ezen a napon te is rendeltél">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
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
          v-if="history[item] !== undefined"
          class=" "
        >
          <span
            v-for="v,k in history[item]"
            :key="k"
            class="badge rounder-pill bg-falusi p-2 py-0"
            :title="v.vendor + 'rendelés lett leadva ezen a napon'"
          >
            @{{ v.vendor }}
          </span>
        </div>
      </div>
      <div
        class="row"
        :class="{'border-3':new Date(item).getDate() === currentDateSelected.getDate()}"
      />
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import { state } from '@/socket';
import { useAuth } from '@/auth';

export default {
  name: 'DateStamp',
  props: {
    'limitToCurrentWeek': Boolean,
    'dateRange': Number(2),
    'history': Object()
  },
  emits: ['selectedDate'],
  setup() {
    const user_states = ref({});
    const weekdates = ref([]);
    const auth = useAuth();
    return {
      user_states,
      weekdates,
      auth
    }
  },
  data() {
    return {
      currentDateSelected: new Date()
    }
  },
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
  mounted() {
    this.getCurrentWeekDates(new Date()).then(res => {
      this.weekdates = res;
      this.getUserBasketStates(this.weekdates[0], this.weekdates[this.weekdates.length -1 ])
    });
  },
  methods: {
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
          "user_id": state.user.id,
          'date_from': day_from,
          'date_to': day_to
        })
      })
        .then(response => response.json())
          .then(data => {
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
    isThereOrder: function (date) {
      for(var i in this.user_states){
          if(this.user_states[i].date == date){
              return true;
          }
      }
      return false;
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
