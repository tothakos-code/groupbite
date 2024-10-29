import axios from "axios";
import { defineStore } from "pinia"
import { notify } from "@kyvg/vue3-notification";
import { useAuth } from "@/stores/auth";
import { useVendorStore } from "@/stores/vendor";

export const useOrderStore = defineStore("order", {
  state: () => ({
    order: {},
    basket: {},
    isLoading: false
  }),
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
        Object.values(person.items).forEach((entry) => {
          sum+= Number(entry.quantity);
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
        Object.values(person.items).forEach((entry) => {
          sum+= Number(entry.quantity) * Number(entry.price);
        })
      })
      sum += Number(this.transportFee);
      return sum;
    },
    userBasketSum(state) {
      const auth = useAuth()
      let sum = 0;
      if (!auth.isLoggedIn) {
        return sum;
      }
      if (state.basket[auth.user.id] === undefined) return sum;

      for (const item of state.basket[auth.user.id].items) {
        sum+= Number(item.quantity) * Number(item.price);
      }

      if (this.userCount != 0) {
        sum += Math.ceil(this.transportFeePerPerson);
      }
      return sum;
    },
    userBasket(state) {
      const auth = useAuth()
      if (!auth.isLoggedIn) {
        return [];
      }
      if (state.basket[auth.user.id] === undefined) return [];
      return state.basket[auth.user.id].items;
    },
    isUserBasketEmpty(state) {
      const auth = useAuth()
      if (!auth.isLoggedIn) {
        return true;
      }
      if (state.basket[auth.user.id] === undefined) return true;
      return state.basket[auth.user.id].items.length == 0;
    },
    transportFee(state) {
      const vendorStore = useVendorStore();
      if (vendorStore.selectedVendor.settings === undefined) {
        return 0;
      }
      return Number(state.order.order_fee)
    }
  },
  actions: {
    async fetch(orderId) {
      this.isLoading = true;
      try {
        const response = await axios.get(`/api/order/${orderId}`);
        this.order = response.data.data;
        return response
      } catch (error) {
        console.error("Failed to get order by ID:", error.response.data.error);
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async fetchHistory(data) {
      this.isLoading = true;
      try {
        const response = await axios.post(`/api/order/history`, data);
        return response
      } catch (error) {
        console.error("Failed to get history:", error.response.data.error);
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async close() {
      this.isLoading = true;
      try {
        const response = await axios.put(`/api/order/${this.order.id}/state`,{
          "state": "closed"
        });
        return response
      } catch (error) {
        console.error("Failed to close order:", error.response.data.error);
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async clearBasket() {
      if ( this.order.state_id === "closed") {
        notify({
          type: "warn",
          text: "A rendelés már el lett küldve. Már nem módosíthatod a kosaradat.",
        });
        return;
      }
      const auth = useAuth()
      try {
        const response = await axios.delete(`/api/order/${this.order.id}/user/${auth.user.id}`)
        return response
      } catch (error) {
        console.error("Failed to clear basket:", error.response.data.error);
        return error.response
      }
    },
    async removeItem(menuItemId, sizeId) {
      if ( this.order.state_id === "closed") {
        notify({
          type: "warn",
          text: "A rendelés már el lett küldve. Már nem módosíthatod a kosaradat.",
        });
        return;
      }
      const auth = useAuth()
      try {
        const response = axios.delete(`/api/order/${this.order.id}/user/${auth.user.id}/item/${menuItemId}/size/${sizeId}`)
        return response
      } catch (error) {
        console.error("Failed to remove item:", error.response.data.error);
        return error.response
      }
    },
    async copy(srcUserId) {
      const auth = useAuth()
      if (!auth.isLoggedIn) {
        notify({
          type: "warn",
          text: "Jelentkezz be a rendeléshez!",
        });
        return;
      }
      if ( this.order.state_id === "closed") {
        notify({
          type: "warn",
          text: "A rendelés már el lett küldve. Már nem módosíthatod a kosaradat.",
        });
        return;
      }
      try {
        const response = axios.put(`/api/order/${this.order.id}/user/${auth.user.id}/copy-from/${srcUserId}`)
        notify({
          type: "info",
          text: "Másolva",
        });
        return response
      } catch (error) {
        console.error("Failed to remove item:", error.response.data.error);
        return error.response
      }
    },
    async addItem(menuItemId, sizeId) {
      const auth = useAuth()
      if (!auth.isLoggedIn) {
        notify({
          type: "warn",
          text: "Jelentkezz be a rendeléshez!",
        });
        return;
      }
      if (this.order.state_id === "closed") {
        notify({
          type: "warn",
          text: "A rendelés már el lett küldve. Már nem módosíthatod a kosaradat.",
        });
        return;
      }
      try {
        const response = axios.put(`/api/order/${this.order.id}/user/${auth.user.id}/item/${menuItemId}/size/${sizeId}`)
        return response
      } catch (error) {
        console.error("Failed to add item:", error.response.data.error);
        return error.response
      }
    },
    async changeTransportPrice(newTransportPrice) {
      try {
        const response = axios.put(`/api/order/${this.order.id}/order_fee`, { "data": {
          "order_fee": newTransportPrice
        } })
        return response
      } catch (error) {
        console.error("Failed to change order_fee:", error.response.data.error);
        return error.response
      }
    }
  }
})
