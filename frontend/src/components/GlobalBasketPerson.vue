<template>
    <div class="card">
      <div class="card-header row d-flex">
        <div class="col-6">
          <span>{{ name }}</span>
        </div>
        <div class="col-6 text-end">
          <span :title="this.basketTotalTitle">{{ this.basketTotal }} Ft</span>
        </div>
      </div>
      <div class="row list-group">
        <div v-for="item in personBasket" :key="item.id" class="list-group-item  d-flex justify-content-between align-items-center">
          <span class="badge bg-warning-subtle border border-warning-subtle text-warning-emphasis rounded-pill">{{ item.quantity }} x</span>
          <span>{{ item.name }}</span>
          <span>{{ item.size }} - {{ item.price }}</span>
        </div>
      </div>
    </div>
</template>

<script>
export default {
  name: 'PersonComponent',
  props: ['name', 'personBasket', 'transportFee'],
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
        console.log(item);
        sum+= Number(item.quantity) * Number((item.price).split(' ')[0]);
        sumTitle+= item.quantity + '*' + item.price + ' + ';
      })
      this.sum = sum + Number(this.transportFee);
      sumTitle+= this.transportFee + ' Ft(Szállítási díj) = ' + this.sum + ' Ft';
      this.sumTitle = sumTitle;
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
