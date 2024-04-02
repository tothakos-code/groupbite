<template>
  <div class="card">
    <div class="card-header">
      <div class="col-3 col-md-6 col-lg-8 row px-0">
        <div class="col-0 d-none col-lg-8 d-lg-inline my-auto truncate ms-0">
          <h2 class="">
            Előző rendelések
          </h2>
        </div>
        <div class="">
          <span>
            <!-- {{ getCurrentMonthName }} {{ currentDateSelected.getWeek() }}. hét -->

          </span>
        </div>
      </div>
      <div class="col-9 col-md-6 col-lg-4 d-flex flex-fill px-0" />
    </div>
    <div class="card-body">
      <div class="">
        <HistoryDateStamp
          class=""
          date-range="3"
          :history="history"
          @selected-date="(date) => getHistroy(date)"
        />
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
        <div
          v-for="(basket, personName) in loaded_menu"
          :key="personName"
          class="row mt-1 mb-1"
        >
          <div class="list-group-item row m-0">
            {{ personName }}
            <GlobalBasketPerson
              :name="personName"
              :person-basket="basket"
              :start-collapsed="true"
              :collapsable="true"
              :copyable="false"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import HistoryDateStamp from './HistoryDateStamp.vue'
import GlobalBasketPerson from './GlobalBasketPerson.vue'
import { useAuth } from '@/auth';
import { transportFeePerPerson, personCount, basketSum, boxCount } from '@/basket';
import axios from 'axios';
import { state } from '@/socket';

export default {
  name: 'FalusiHistroy',
  components: {
    HistoryDateStamp,
    GlobalBasketPerson,
  },
  emits: ['close'],
  setup() {
    const auth = useAuth();
    return {
      auth,
      transportFeePerPerson,
      personCount,
      basketSum,
      boxCount
    }
  },
  data() {
    return {
      history: {},
      selected_history: new Date(),
      loaded_menu: {},
      sum: 0,
      user_avg: 0,
      user_avg_p_day: 0,
    }
  },
  mounted() {
    this.getHistroy();
  },
  methods: {
    getHistroy: function() {
      // this.getCurrentMonthName(date)
      let url = `http://${window.location.host}/api/order/history`
      axios.post(url, {
          'date_from': '2024-03-25',
          'date_to': '2024-03-31',
          'user_id': state.user.id
        })
        .then((data) => {
          this.history = data.data;
          console.log(this.history);
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
    }
    // getCurrentMonthName(date) {
    //   return date.toLocaleDateString('hu-HU', {month:'long'});
    // }
  }
}
</script>

<style>

</style>
