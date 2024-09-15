import axios from "axios";
import { defineStore } from "pinia"
import { notify } from "@kyvg/vue3-notification";

export const useSizeStore = defineStore("size", {
  state: () => ({
    isLoading: false
  }),
  getters: {

  },
  actions: {
    async update(sizeId, data) {
      this.isLoading = true;
      try {
        const response = await axios.put(`/api/size/${sizeId}`, { "data":data });
        notify({
          type: "info",
          text: "Méret frissítés sikeres!",
        });
        return response
      } catch (error) {
        console.error("Failed to update size:", error.response.data.error);
        notify({
          type: "error",
          text: "Méret frissítés nem sikerült!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async delete(sizeId) {
      this.isLoading = true;
      try {
        const response = await axios.delete(`/api/size/${sizeId}`);
        notify({
          type: "info",
          text: "Méret törlés sikeres!",
        });
        return response
      } catch (error) {
        console.error("Failed to delete size:", error.response.data.error);
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
        const response = await axios.post(`/api/size`, { "data":data });
        notify({
          type: "info",
          text: "Méret hozzáadása sikeres!",
        });
        return response

      } catch (error) {
        console.error("Failed to add size:", error.response.data.error);
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
