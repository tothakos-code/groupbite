import axios from "axios";
import { defineStore } from "pinia"
import { notify } from "@kyvg/vue3-notification";

export const useItem = defineStore("item", {
  state: () => ({
    isLoading: false
  }),
  getters: {

  },
  actions: {
    async update(data) {
      this.isLoading = true;
      try {
        const response = await axios.post(`/api/item/update`, {"data":data});
        notify({
          type: "info",
          text: "Étel frissítés sikeres!",
        });
        return response
      } catch (error) {
        console.error("Failed to update menu",error);
        notify({
          type: "error",
          text: "Étel frissítés nem sikerült!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async delete(data) {
      this.isLoading = true;
      try {
        const response = await axios.post(`/api/item/delete`, {"data":data});
        notify({
          type: "info",
          text: "Étel törlés sikeres!",
        });
        return response
      } catch (error) {
        console.error("Failed to delete menu",error);
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
        const response = await axios.post(`/api/item/add`, {"data":data});
        notify({
          type: "info",
          text: "Étel hozzáadása sikeres!",
        });
        return response

      } catch (error) {
        console.error("Failed to add menu",error);
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
