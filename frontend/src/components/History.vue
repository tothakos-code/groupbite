<template>
  <div class="card">
    <div class="card-header row d-flex">
      <div class="col-6 d-flex justify-content-start ps-0">
        <a href="#" class="btn btn-link link-underline link-underline-opacity-0 link-warning border rounded pt-2" @click="this.$emit('close')">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-caret-left" viewBox="0 0 16 16">
          <path d="M10 12.796V3.204L4.519 8 10 12.796zm-.659.753-5.48-4.796a1 1 0 0 1 0-1.506l5.48-4.796A1 1 0 0 1 11 3.204v9.592a1 1 0 0 1-1.659.753z"/>
        </svg>
        Vissza
        </a>
        <h2 class="ps-2">Előző rendelések</h2>
      </div>
      <div class="col-6">
        <Datestamp @selectedDate="(date) => this.getHistroy(date)"/>
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
                :collapsable="true">
              </GlobalBasketPerson>
            </div>
          </div>
      </div>
    </div>
  </div>
</template>

<script>
import Datestamp from './DateStamp.vue'
import { socket } from "@/socket";
import GlobalBasketPerson from './GlobalBasketPerson.vue'

export default {
  name: 'FalusiHistroy',
  components: {
    Datestamp,
    GlobalBasketPerson
  },
  emits: ['close'],
  methods: {
    getHistroy: function(date) {
      // fr-CA time locale is in the same format that the db use
      let formatedDate = date.toLocaleDateString("fr-CA", {year:"numeric", month: "2-digit", day:"2-digit"});
      socket.emit('Order History', {'requestedDate':formatedDate}, (result) => {
        this.history = result;
      });
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
      sum += Number(this.transportFeePerPerson);
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
    }
  }
}
</script>

<style>
</style>
