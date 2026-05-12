import axios from "axios";
import { defineStore } from "pinia";

export const useOptionGroupsStore = defineStore("option_groups", {
  state: () => ({
    byVendor: {},
  }),
  getters: {
    forVendor: (state) => (vendorId) => state.byVendor[vendorId] || [],
  },
  actions: {
    async fetchByVendor(vendorId) {
      try {
        const response = await axios.get(`/api/vendor/${vendorId}/option-groups`);
        this.byVendor[vendorId] = response.data.data;
      } catch (error) {
        console.error("Failed to fetch option groups:", error);
      }
    },
    async createGroup(vendorId, data) {
      const response = await axios.post(`/api/vendor/${vendorId}/option-groups`, { data });
      await this.fetchByVendor(vendorId);
      return response;
    },
    async updateGroup(vendorId, groupId, data) {
      const response = await axios.put(`/api/vendor/${vendorId}/option-groups/${groupId}`, { data });
      await this.fetchByVendor(vendorId);
      return response;
    },
    async deleteGroup(vendorId, groupId) {
      const response = await axios.delete(`/api/vendor/${vendorId}/option-groups/${groupId}`);
      await this.fetchByVendor(vendorId);
      return response;
    },
    async addChoice(vendorId, groupId, data) {
      const response = await axios.post(`/api/vendor/${vendorId}/option-groups/${groupId}/choices`, { data });
      await this.fetchByVendor(vendorId);
      return response;
    },
    async updateChoice(vendorId, groupId, choiceId, data) {
      const response = await axios.put(`/api/vendor/${vendorId}/option-groups/${groupId}/choices/${choiceId}`, { data });
      await this.fetchByVendor(vendorId);
      return response;
    },
    async deleteChoice(vendorId, groupId, choiceId) {
      const response = await axios.delete(`/api/vendor/${vendorId}/option-groups/${groupId}/choices/${choiceId}`);
      await this.fetchByVendor(vendorId);
      return response;
    },
    async assignToItem(itemId, groupId, index = 0) {
      const response = await axios.post(`/api/item/${itemId}/option-groups/${groupId}`, { index });
      return response;
    },
    async unassignFromItem(itemId, groupId) {
      const response = await axios.delete(`/api/item/${itemId}/option-groups/${groupId}`);
      return response;
    },
  },
});
