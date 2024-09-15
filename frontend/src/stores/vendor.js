import axios from "axios";
import { defineStore } from "pinia"
import { notify } from "@kyvg/vue3-notification";

export const useVendorStore = defineStore("vendor", {
  state: () => ({
    vendors: [],
    selectedVendor: undefined,
    isLoading: false
  }),
  getters: {

  },
  actions: {
    async fetch() {
      this.isLoading = true;
      try {
        const response = await axios.get(`/api/vendor`);
        return response
      } catch (error) {
        console.error("Failed to fetch vendors",error);
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async fetchActive() {
      this.isLoading = true;
      try {
        const response = await axios.get(`/api/vendor/active`);
        this.vendors = response.data.data;
        return response
      } catch (error) {
        console.error("Failed to fetch vendors",error);
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async add(data) {
      this.isLoading = true;
      try {
        const response = await axios.post(`/api/vendor`, {"data":data});
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
    async activate(vendorId) {
      this.isLoading = true;
      try {
        const response = await axios.put(`/api/vendor/${vendorId}/activate`);
        return response
      } catch (error) {
        console.error("Failed to activate vendor", error);
        notify({
          type: "error",
          text: "Vendor aktiválás nem sikerült!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async deactivate(vendorId) {
      this.isLoading = true;
      try {
        const response = await axios.put(`/api/vendor/${vendorId}/deactivate`);
        return response
      } catch (error) {
        console.error("Failed to deactivate vendor", error);
        notify({
          type: "error",
          text: "Vendor deaktiválás nem sikerült!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async fetchVendor(vendorId) {
      this.isLoading = true;
      try {
        const response = await axios.get(`/api/vendor/${vendorId}`);
        return response
      } catch (error) {
        console.error("Failed to get vendor by ID", error);
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async saveSettings(vendorId, data) {
      this.isLoading = true;
      try {
        const response = await axios.put(`/api/vendor/${vendorId}/settings`, { "data": data});
        notify({
          type: "info",
          text: "Beállítások mentése sikeres!",
        });
        return response
      } catch (error) {
        console.error("Failed to update vendor settings", error);
        notify({
          type: "error",
          text: "Beállítások mentése nem sikerült!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
  }
})
