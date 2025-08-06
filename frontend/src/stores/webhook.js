import axios from "axios";
import { defineStore } from "pinia"
import { notify } from "@kyvg/vue3-notification";

export const useWebhookStore = defineStore("webhook", {
  state: () => ({
    isLoading: false
  }),
  getters: {

  },
  actions: {
    async update(webhookId, data) {
      this.isLoading = true;
      try {
        const response = await axios.put(`/api/webhook/${webhookId}`, { "data":data });
        return response
      } catch (error) {
        console.error("Failed to update webhook:", error.response.data.error);
        notify({
          type: "error",
          text: "Webhook frissítés nem sikerült!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async delete(webhookId) {
      this.isLoading = true;
      try {
        const response = await axios.delete(`/api/webhook/${webhookId}`);
        notify({
          type: "info",
          text: "Webhook törlés sikeres!",
        });
        return response
      } catch (error) {
        console.error("Failed to delete webhook:", error.response.data.error);
        notify({
          type: "error",
          text: "Webhook törlés nem sikerült!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async add(data) {
      this.isLoading = true;
      try {
        const response = await axios.post(`/api/webhook`, { "data":data });
        return response

      } catch (error) {
        console.error("Failed to add webhook:", error.response.data.error);
        notify({
          type: "error",
          text: "Webhook hozzáadása nem sikerült!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async test(data) {
      this.isLoading = true;
      try {
        const response = await axios.post(`/api/webhook/test`, { "data":data });
        return response

      } catch (error) {
        console.error("Failed to test webhook:", error.response.data.error);
        notify({
          type: "error",
          text: "Webhook validációs hiba!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
  }
})
