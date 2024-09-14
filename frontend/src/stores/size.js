import axios from "axios";
import { defineStore } from "pinia"
import { notify } from "@kyvg/vue3-notification";

export const useSize = defineStore("size", {
  state: () => ({
    isLoading: false
  }),
  getters: {

  },
  actions: {
    async update(data) {
      this.isLoading = true;
      try {
        const response = await axios.post(`/api/size/update`, {"data":data});
        notify({
          type: "info",
          text: "Méret frissítés sikeres!",
        });
        return response
      } catch (error) {
        console.error("Failed to update size",error);
        notify({
          type: "error",
          text: "Méret frissítés nem sikerült!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async delete(data) {
      this.isLoading = true;
      try {
        const response = await axios.post(`/api/size/delete`, {"data":data});
        notify({
          type: "info",
          text: "Méret törlés sikeres!",
        });
        return response
      } catch (error) {
        console.error("Failed to delete size",error);
        notify({
          type: "error",
          text: "Méret törlés nem sikerült!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async add(data) {
      this.isLoading = true;
      try {
        const response = await axios.post(`/api/size/add`, {"data":data});
        notify({
          type: "info",
          text: "Méret hozzáadása sikeres!",
        });
        return response

      } catch (error) {
        console.error("Failed to add size",error);
        notify({
          type: "error",
          text: "Méret hozzáadása nem sikerült!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
  }
})
