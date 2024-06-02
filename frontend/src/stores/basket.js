import { state as vuestate, socket } from "@/socket.js";
import { defineStore } from 'pinia'
import { notify } from "@kyvg/vue3-notification";
import axios from 'axios';
import { useAuth } from "@/stores/auth";



export const useBasket = defineStore('basket', {
  state: () => ({basket: {}}),
  getters: {
    userCount(state) {
      return Object.keys(state.basket).length;
    },
    transportFeePerPerson() {
      if (this.userCount == 0) {
        return 0;
      }
      return Math.ceil(this.transportFee / this.userCount);
    },
    itemCount(state) {
      let sum=0;
      Object.values(state.basket).forEach((person) => {
        Object.values(person.basket_entry).forEach((entry) => {
          sum+= Number(entry.count);
        })
      })
      return sum;
    },
    totalSum(state) {
      if (this.userCount == 0) {
        return 0;
      }
      let sum=0;
      Object.values(state.basket).forEach((person) => {
        Object.values(person.basket_entry).forEach((entry) => {
          sum+= Number(entry.count) * Number(entry.item.price);
        })
      })
      sum += Number(this.transportFee);
      return sum;
    },
    userBasketSum(state) {
      const auth = useAuth()
      let sum = 0;
      if (state.basket[auth.user.id] === undefined) return sum;

      for (const item of state.basket[auth.user.id].basket_entry) {
        sum+= Number(item.count) * Number(item.item.price);
      }

      if (this.userCount != 0) {
        sum += Math.ceil(this.transportFeePerPerson);
      }
      return sum;
    },
    userBasket(state) {
      const auth = useAuth()
      if (state.basket[auth.user.id] === undefined) return [];
      return state.basket[auth.user.id].basket_entry;
    },
    isUserBasketEmpty(state) {
      const auth = useAuth()
      if (state.basket[auth.user.id] === undefined) return true;
      return state.basket[auth.user.id].basket_entry.length == 0;
    },
    transportFee() {
      return Number(vuestate.selected_vendor.settings.transport_price.value)
    }
  },
  actions: {
    clearBasket() {
      if ( vuestate.orderState === 'closed') {
        notify({
          type: "warn",
          text: "A rendelés már el lett küldve. Már nem módosíthatod a kosaradat.",
        });
        return;
      }
      const auth = useAuth()
      axios.post(`http://${window.location.host}/api/order/${vuestate.order.id}/clear`,{
        "user_id": auth.user.id
      })
    },
    removeItem(menuItem_id) {
      if ( vuestate.order.state_id === 'closed') {
        notify({
          type: "warn",
          text: "A rendelés már el lett küldve. Már nem módosíthatod a kosaradat.",
        });
        return;
      }
      const auth = useAuth()
      axios.post(`http://${window.location.host}/api/order/${vuestate.order.id}/remove`,{
        "user_id": auth.user.id,
        "menu_item_id": menuItem_id
      })
    },
    copy() {
      const auth = useAuth()
      if (!auth.isLoggedIn) {
        notify({
          type: "warn",
          text: "Jelentkezz be a rendeléshez!",
        });
        return;
      }
      socket.emit("Server Basket Update", { "userid": auth.user.id, "basket": this.personBasket, "order_date": vuestate.selectedDate.toISOString().split('T')[0] });
      notify({
        type: "info",
        text: "Másolva",
      });
    },
    addItem(menuItem_id) {
      const auth = useAuth()
      if (!auth.isLoggedIn) {
        notify({
          type: "warn",
          text: "Jelentkezz be a rendeléshez!",
        });
        return;
      }
      if (vuestate.order.state_id === 'closed') {
        notify({
          type: "warn",
          text: "A rendelés már el lett küldve. Már nem módosíthatod a kosaradat.",
        });
        return;
      }
      if (this.currentUserState === 'skip') {
        socket.emit("User Daily State Change",{ 'id': auth.user.id, 'new_state':'none' });
      }
      axios.post(`http://${window.location.host}/api/order/${vuestate.order.id}/add`,{
        "user_id": auth.user.id,
        "menu_item_id": menuItem_id
      })
    }
  }
})
