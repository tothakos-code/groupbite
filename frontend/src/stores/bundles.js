import axios from "axios";
import { defineStore } from "pinia";

export const useBundlesStore = defineStore("bundles", {
  state: () => ({
    byVendor: {},
  }),
  getters: {
    forVendor: (state) => (vendorId) => state.byVendor[vendorId] || [],
  },
  actions: {
    async fetchByVendor(vendorId) {
      try {
        const response = await axios.get(`/api/vendor/${vendorId}/bundles`);
        this.byVendor[vendorId] = response.data.data;
      } catch (error) {
        console.error("Failed to fetch bundles:", error);
      }
    },
    async createBundle(vendorId, data) {
      const response = await axios.post(`/api/vendor/${vendorId}/bundles`, { data });
      await this.fetchByVendor(vendorId);
      return response;
    },
    async updateBundle(vendorId, bundleId, data) {
      const response = await axios.put(`/api/vendor/${vendorId}/bundles/${bundleId}`, { data });
      await this.fetchByVendor(vendorId);
      return response;
    },
    async deleteBundle(vendorId, bundleId) {
      const response = await axios.delete(`/api/vendor/${vendorId}/bundles/${bundleId}`);
      await this.fetchByVendor(vendorId);
      return response;
    },
    async addSlot(vendorId, bundleId, data) {
      const response = await axios.post(`/api/vendor/${vendorId}/bundles/${bundleId}/slots`, { data });
      await this.fetchByVendor(vendorId);
      return response;
    },
    async updateSlot(vendorId, bundleId, slotId, data) {
      const response = await axios.put(`/api/vendor/${vendorId}/bundles/${bundleId}/slots/${slotId}`, { data });
      await this.fetchByVendor(vendorId);
      return response;
    },
    async deleteSlot(vendorId, bundleId, slotId) {
      const response = await axios.delete(`/api/vendor/${vendorId}/bundles/${bundleId}/slots/${slotId}`);
      await this.fetchByVendor(vendorId);
      return response;
    },
  },
});
