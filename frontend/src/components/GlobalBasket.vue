<template>
  <div class="card">
      <div class="align-items-center card-header row d-flex">
        <div class="col-3">
          <span class="fs-2">Közös kosár</span>
        </div>
        <div class="col-3 align-items-center">
          <span class="row">{{ totalSum }} Ft</span>
          <span class="row">{{ boxCount }} db doboz</span>
        </div>
        <div class="col-3 align-items-center">
          <span class="row">
            {{ this.transportFeePerPerson }} Ft szállítás díj/fő
          </span>
          <span class="row">
            {{ this.personCount }} fő
          </span>
        </div>
        <div class="col-3">
          <TransferPopup/>
        </div>
      </div>
      <div
        v-for="(value, key) in this.waitingFor"
        :key="key"
        class="row mt-1 mb-1">
        <div class="card">
          <div v-if="value == 'sub'" class="card-header row d-flex bg-danger-subtle">
            <div class="col-6">
              <span>{{ key }}</span>
            </div>
            <div class="col-6 text-end">
              <span>Még nem választott</span>
            </div>
          </div>
          <div v-if="value == 'video'" class="card-header row d-flex bg-warning-subtle">
            <div class="col-6">
              <span>{{ key }}</span>
            </div>
            <div class="col-6 text-end">
              <span>Videóra vár</span>
            </div>
          </div>
        </div>
      </div>
      <div
        v-for="(basket, personName) in this.globalBasket"
        :key="personName"
        class="row mt-1 mb-1">
        <GlobalBasketPerson
          :name="personName"
          :personBasket="basket"
          :transportFee='this.transportFeePerPerson'>
        </GlobalBasketPerson>
      </div>
  </div>
</template>

<script>
import { state } from "@/socket";
import GlobalBasketPerson from './GlobalBasketPerson.vue'
import TransferPopup from './TransferPopup.vue'

export default {
  name: 'GlobalBasket',
  components: {
    TransferPopup,
    GlobalBasketPerson
  },
  data() {
    return {
      transportFee: 400
    };
  },
  computed: {
    globalBasket() {
      return state.globalBasket;
    },
    waitingFor() {
      const userStates = structuredClone(state.userStates);
      let pickedList = Object.keys(state.globalBasket)

      for (const [key, value] of Object.entries(state.userStates)) {
        if (value === 'none' || value === 'skip') {
          delete userStates[key];
        }
        if (pickedList.includes(key)) {
          delete userStates[key];
        }
      }
      return userStates;
    },
    totalSum() {
      if (this.personCount == 0) {
        return 0;
      }
      let sum=0;
      Object.values(this.globalBasket).forEach((person) => {
        Object.values(person).forEach((item) => {
          sum+= Number(item.quantity) * Number((item.price).split(' ')[0]);
        })
      })
      sum += Number(this.transportFee);
      return sum;
    },
    boxCount() {
      let sum=0;
      Object.values(this.globalBasket).forEach((person) => {
        Object.values(person).forEach((item) => {
          sum+= Number(item.quantity);
        })
      })
      return sum;
    },
    personCount() {
      return Object.keys(state.globalBasket).length;
    },
    transportFeePerPerson() {
      if (this.personCount == 0) {
        return 0;
      }
      return Math.ceil(this.transportFee/ this.personCount);
    }
  },
  methods: {
    // calculateSum: function(personBasket) {
    //   let sum=0;
    //   Object.entries(basket).forEach(([id, item]) => {
    //     sum+= Number(item.quantity) * Number((item.price).split(' ')[0]);
    //   },
    //   return sum + transportFee;
    // }
  }
}
</script>

<style>
</style>
