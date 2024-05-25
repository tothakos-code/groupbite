import { state } from "@/socket.js";
import { computed } from "vue";


export const personCount = computed(() => {
    return Object.keys(state.basket).length;
  });

export const transportFeePerPerson = computed(() => {
    if (personCount.value == 0) {
      return 0;
    }
    return Math.ceil(state.selected_vendor.settings.transport_price.value / personCount.value);
  });

export const boxCount = computed(() => {
    let sum=0;
    Object.values(state.basket).forEach((person) => {
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
    Object.values(state.basket).forEach((person) => {
      Object.values(person.basket_entry).forEach((entry) => {
        sum+= Number(entry.count) * Number(entry.item.price);
      })
    })
    sum += Number(state.selected_vendor.settings.transport_price.value);
    return sum;
});
