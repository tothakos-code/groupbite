import axios from "axios";
import { defineStore } from "pinia";

export const useCategoriesStore = defineStore("categories", {
  state: () => ({
    byVendor: {},
  }),
  getters: {
    namesForVendor: (state) => (vendorId) =>
      (state.byVendor[vendorId] || []).map((c) => c.name),
  },
  actions: {
    async fetchByVendor(vendorId) {
      try {
        const response = await axios.get(`/api/vendor/${vendorId}/categories`);
        this.byVendor[vendorId] = response.data.data;
      } catch (error) {
        console.error("Failed to fetch categories:", error);
      }
    },
    async createCategory(vendorId, name) {
      const response = await axios.post(`/api/vendor/${vendorId}/categories`, { data: { name } });
      await this.fetchByVendor(vendorId);
      return response;
    },
    async renameCategory(vendorId, categoryId, name, defaultPackagingFee = null) {
      const response = await axios.put(`/api/vendor/${vendorId}/categories/${categoryId}`, {
        data: { name, default_packaging_fee: defaultPackagingFee ?? 0 },
      });
      await this.fetchByVendor(vendorId);
      return response;
    },
    async deleteCategory(vendorId, categoryId) {
      const response = await axios.delete(`/api/vendor/${vendorId}/categories/${categoryId}`);
      await this.fetchByVendor(vendorId);
      return response;
    },
  },
});
