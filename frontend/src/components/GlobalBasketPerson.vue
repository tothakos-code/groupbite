<template>
    <div class="card">
      <div class="card-header row d-flex pe-0">
        <div class="col-6">
          <span>{{ name }}</span>
          <a v-if="copyable && name !== loggedInUser" class="ms-2 p-1 btn btn-warning" @click="copy">Másol</a>
        </div>
        <div class="col-6 d-flex justify-content-end">
          <span class="me-2" :title="this.basketTotalTitle">{{ this.basketTotal }} Ft</span>
          <a v-if="collapsable" class="link-underline link-underline-opacity-0" data-bs-toggle="collapse" :data-bs-target="'#' + (name.replace(/[^a-z0-9]/ig, ''))" role="button" :aria-expanded="!collapsable || !startCollapsed" :aria-controls="name">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-caret-down" viewBox="0 0 16 16">
              <path d="M3.204 5h9.592L8 10.481 3.204 5zm-.753.659 4.796 5.48a1 1 0 0 0 1.506 0l4.796-5.48c.566-.647.106-1.659-.753-1.659H3.204a1 1 0 0 0-.753 1.659z"/>
            </svg>
          </a>
        </div>
      </div>
      <div class="row list-group" :class="{ show: !collapsable || !startCollapsed, collapse: startCollapsed}" :id="collapsable ? (name.replace(/[^a-z0-9]/ig, '')) : false">
        <div v-for="item in personBasket" :key="item.id" class="list-group-item  d-flex justify-content-between align-items-center"  >
          <span class="badge bg-warning-subtle border border-warning-subtle text-warning-emphasis rounded-pill">{{ item.quantity }} x</span>
          <span>{{ item.name }}</span>
          <span>{{ item.size }} - {{ item.price }}</span>
        </div>
      </div>
    </div>
</template>

<script>
import { state } from "@/socket";

export default {
  name: 'PersonComponent',
  props: {
    'name':{
      type: String
    },
    'personBasket':{
      type: Object
    },
    'transportFee':{
      type: Number,
      default: 400
    },
    'startCollapsed':{
      type: Boolean,
      default: false
    },
    'collapsable':{
      type: Boolean,
      default: true
    },
    'copyable':{
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      sum: 0
    };
  },
  mounted() {
    this.calculateSum()
  },
  methods: {
    calculateSum: function() {
      let sum=0;
      let sumTitle = ""
      Object.entries(this.personBasket).forEach(([id,item]) => {
        console.log(id);
        sum+= Number(item.quantity) * Number((item.price).split(' ')[0]);
        sumTitle+= item.quantity + '*' + item.price + ' + ';
      })
      this.sum = sum + Number(this.transportFee);
      sumTitle+= this.transportFee + ' Ft(Szállítási díj) = ' + this.sum + ' Ft';
      this.sumTitle = sumTitle;
    },
    copy: function() {
      state.localBasket = this.personBasket;
    }
  },
  computed: {
    basketTotal() {
      let sum=0;
      // let sumTitle = ""
      Object.values(this.personBasket).forEach((item) => {
        sum+= Number(item.quantity) * Number((item.price).split(' ')[0]);
        // sumTitle+= item.quantity + '*' + item.price + ' + ';
      })
      sum += Number(this.transportFee);
      // sumTitle+= this.transportFee + ' Ft(Szállítási díj) = ' + this.sum + ' Ft';
      // this.sumTitle = sumTitle;
      return sum;
    },
    basketTotalTitle() {
      let sumTitle = ""
      Object.values(this.personBasket).forEach((item) => {
        sumTitle+= item.quantity + '*' + item.price + ' + ';
      })
      sumTitle+= this.transportFee + ' Ft(Szállítási díj) = ' + this.sum + ' Ft';
      return sumTitle;
    },
    loggedInUser() {
      return state.user.username
    }
  }
}
</script>

<style>
.globalList div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px;
  border: 1px solid #ccc;
}
</style>
