import axios from "axios";
import { defineStore } from "pinia"
import { notify } from "@kyvg/vue3-notification";

export const useItemStore = defineStore("item", {
  state: () => ({
    isLoading: false
  }),
  getters: {

  },
  actions: {
    async update(itemId, data) {
      this.isLoading = true;
      try {
        const response = await axios.put(`/api/item/${itemId}`, { "data":data });
        notify({
          type: "info",
          text: "Étel frissítés sikeres!",
        });
        return response
      } catch (error) {
        console.error("Failed to update item:", error.response.data.error);
        notify({
          type: "error",
          text: "Étel frissítés nem sikerült!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async delete(itemId) {
      this.isLoading = true;
      try {
        const response = await axios.delete(`/api/item/${itemId}`);
        notify({
          type: "info",
          text: "Étel törlés sikeres!",
        });
        return response
      } catch (error) {
        console.error("Failed to delete item:", error.response.data.error);
        notify({
          type: "error",
          text: "Étel törlés nem sikerült!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async add(data) {
      this.isLoading = true;
      try {
        const response = await axios.post(`/api/item`, { "data":data });
        notify({
          type: "info",
          text: "Étel hozzáadása sikeres!",
        });
        return response

      } catch (error) {
        console.error("Failed to add item:", error.response.data.error);
        notify({
          type: "error",
          text: "Étel hozzáadása nem sikerült!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
  }
})
