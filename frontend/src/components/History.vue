<template>
  <div class="card">
    <div class="card-header row d-flex">
      <div class="col-3 col-md-6 col-lg-8 row px-0">
        <div class="col-12 col-lg-4 my-auto">
          <a href="#" class="btn btn-link link-underline link-underline-opacity-0 border rounded pt-2" :class="['link-' + this.userColor ]" @click="this.$emit('close')">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-caret-left" viewBox="0 0 16 16">
              <path d="M10 12.796V3.204L4.519 8 10 12.796zm-.659.753-5.48-4.796a1 1 0 0 1 0-1.506l5.48-4.796A1 1 0 0 1 11 3.204v9.592a1 1 0 0 1-1.659.753z"/>
            </svg>
            Vissza
          </a>
        </div>
        <div class="col-0 d-none col-lg-8 d-lg-inline my-auto truncate ms-0">
          <h2 class="">Előző rendelések</h2>
        </div>
      </div>
      <div class="col-9 col-md-6 col-lg-4 d-flex flex-fill px-0">
        <Datestamp @selected-date="(date) => this.getHistroy(date)"/>
      </div>
    </div>
    <div class="row">
      <div class="col">
          <div class="row d-flex my-1">
            <div class="col text-center align-center">
              <span class="btn pe-none border border-secondary-subtle rounded">{{ totalSum }} Ft</span>
            </div>
            <div class="col text-center">
              <span class="btn pe-none border border-secondary-subtle rounded">{{ boxCount }} db doboz</span>
            </div>
            <div class="col text-center">
              <span class="btn pe-none border border-secondary-subtle rounded">
                {{ this.transportFeePerPerson }} Ft szállítás díj/fő
              </span>
            </div>
            <div class="col text-center">
              <span class="btn pe-none border border-secondary-subtle rounded">
                {{ this.personCount }} fő
              </span>
            </div>

          </div>
          <div
            v-for="(basket, personName) in history"
            :key="personName"
            class="row mt-1 mb-1">
            <div class="list-group-item row m-0">
              <GlobalBasketPerson
                :name="personName"
                :personBasket="basket"
                :transportFee='this.transportFeePerPerson'
                :startCollapsed="true"
                :collapsable="true"
                :copyable="false">
              </GlobalBasketPerson>
            </div>
          </div>
      </div>
    </div>
  </div>
</template>

<script>
import Datestamp from './DateStamp.vue'
import GlobalBasketPerson from './GlobalBasketPerson.vue'
import { state } from '@/socket';

export default {
  name: 'FalusiHistroy',
  components: {
    Datestamp,
    GlobalBasketPerson
  },
  emits: ['close'],
  methods: {
    getHistroy: function(date) {
      let url = ''
      if (date === undefined) {
        url = `http://${window.location.host}/api/order/history`
      } else {
        url = `http://${window.location.host}/api/order/history/${new Date(date).toISOString().split('T')[0]}`
      }
      fetch(url)
        .then(response => response.json())
          .then(data => {
            this.history = data;
          })
        .catch(error => console.error(error));
    }
  },
  data() {
    return {
      history: {}
    }
  },
  mounted() {
    this.getHistroy(new Date());
  },
  computed: {
    totalSum() {
      if (this.personCount == 0) {
        return 0;
      }
      let sum=0;
      Object.values(this.history).forEach((person) => {
        Object.values(person).forEach((item) => {
          sum+= Number(item.quantity) * Number((item.price).split(' ')[0]);
        })
      })
      // transport fee, this sould be an constatnt or saved in the db if it changes
      sum += 400;
      return sum;
    },
    boxCount() {
      if (!this.history || this.history === undefined || this.history === null) {
        return 0;
      }
      let sum=0;
      Object.values(this.history).forEach((person) => {
        Object.values(person).forEach((item) => {
          sum+= Number(item.quantity);
        })
      })
      return sum;
    },
    personCount() {
      if (!this.history || this.history === undefined || this.history === null) {
        return 0;
      }
      return Object.keys(this.history).length;
    },
    transportFeePerPerson() {
      if (this.personCount == 0) {
        return 0;
      }
      return Math.ceil(400 / this.personCount);
    },
    userColor() {
      return state.user.ui_color ? state.user.ui_color : "falusi";
    }
  }
}
</script>

<style>
</style>
