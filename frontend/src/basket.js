import { state } from "@/socket.js";
import { computed, ref } from "vue";

export const transportFee = ref(0);

export const personCount = computed(() => {
    return Object.keys(state.globalBasket).length;
  });

export const transportFeePerPerson = computed(() => {
    if (personCount.value == 0) {
      return 0;
    }
    return Math.ceil(transportFee.value / personCount.value);
  });

export const boxCount = computed(() => {
    let sum=0;
    Object.values(state.globalBasket).forEach((person) => {
      Object.values(person).forEach((item) => {
        sum+= Number(item.quantity);
      })
    })
    return sum;
  });

export const basketSum = computed(() => {
    if (personCount.value == 0) {
      return 0;
    }
    let sum=0;
    Object.values(state.globalBasket).forEach((person) => {
      Object.values(person).forEach((item) => {
        sum+= Number(item.quantity) * Number((item.price).split(' ')[0]);
      })
    })
    sum += Number(transportFee.value);
    return sum;
});
