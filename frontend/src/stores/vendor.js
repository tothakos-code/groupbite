import axios from "axios";
import { defineStore } from "pinia"
import { notify } from "@kyvg/vue3-notification";
import { requestNotificationPermission } from "@/main";
import { useAuth } from "@/stores/auth";

export const useVendorStore = defineStore("vendor", {
  state: () => ({
    vendors: [],
    selectedVendor: undefined,
    isLoading: false,
    routesLoaded: false
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
        console.error("Failed to fetch vendors:", error.response.data.error);
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async fetchMenus(vendorId, querryParams) {
      this.isLoading = true;
      try {
        const response = await axios.get(`/api/vendor/${vendorId}/menus`,
          { "params": querryParams }
        );
        return response
      } catch (error) {
        console.error("Failed to fetch vendors:", error.response.data.error);
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async add(data) {
      this.isLoading = true;
      try {
        const response = await axios.post(`/api/vendor`, { "data": data });
        notify({
          type: "info",
          text: "Üzlet hozzáadása sikeres!",
        });
        return response

      } catch (error) {
        console.error("Failed to add size:", error.response.data.error);
        notify({
          type: "error",
          text: "Üzlet hozzáadása nem sikerült!",
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
        console.error("Failed to activate vendor:", error.response.data.error);
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
        console.error("Failed to deactivate vendor:", error.response.data.error);
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
        console.error("Failed to get vendor by ID:", error.response.data.error);
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async import(vendorId, formData) {
      this.isLoading = true;
      try {
        const response = await axios.post(`/api/vendor/${vendorId}/menus/import`,
          formData,
          {
            headers: {
                "Content-Type": "multipart/form-data"
            }
          }
        );
        notify({
          type: "info",
          text: "Menü importálás sikeres!",
        });
        return response
      } catch (error) {
        console.error("Failed to upload JSON:", error.response.data.error);
        notify({
          type: "error",
          text: "Menü importálása nem sikerült!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async saveSettings(vendorId, data) {
      this.isLoading = true;
      try {
        const response = await axios.put(`/api/vendor/${vendorId}/settings`, { "data": data });
        notify({
          type: "info",
          text: "Beállítások mentése sikeres!",
        });
        return response
      } catch (error) {
        console.error("Failed to update vendor settings:", error.response.data.error);
        notify({
          type: "error",
          text: "Beállítások mentése nem sikerült!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async scan(vendorId, data) {
      this.isLoading = true;
      try {
        const response = await axios.get(`/api/vendor/${vendorId}/scan?menu_date=${data}`);
        notify({
          type: "info",
          text: "Scan sikeres!",
        });
        return response
      } catch (error) {
        console.error("Failed to run scan on vendor:", error.response.data.error);
        notify({
          type: "error",
          text: "Scan nem sikerült!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async subscribe(){
      const auth = useAuth()
      if (!auth.isLoggedIn) {
        notify({
          type: "warn",
          text: "Jelentkezz be a rendeléshez!",
        });
        return;
      }
      try {
        await requestNotificationPermission();

        const publicKey = await axios.get("/vapid_public_key");
        const registration = await navigator.serviceWorker.ready;

        const subscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: publicKey.data
        });

        await axios.post(`/api/vendor/${this.selectedVendor.id}/notifications/reminder/subscribe`,
          { "data": subscription }
        );

        notify({
          type: "info",
          text: `Bekapcsoltad a(z) ${this.selectedVendor.name} értesítést!`,
        });

      } catch (error) {
        console.error("Failed to subscribe to notification:", error);
        notify({
          type: "error",
          text: "Értesítés beállítása nem sikerült!",
        });
      } finally {
        this.isLoading = false;
      }
    },
    async unsubscribe() {
      const auth = useAuth()
      if (!auth.isLoggedIn) {
        notify({
          type: "warn",
          text: "Jelentkezz be a rendeléshez!",
        });
        return;
      }
      try {
        const response = await axios.delete(`/api/vendor/${this.selectedVendor.id}/notifications/reminder/unsubscribe`)
        notify({
          type: "info",
          text: `Kikapcsoltad a(z) ${this.selectedVendor.name} értesítést!`,
        });
        return response
      } catch (error) {
        console.error("Failed to unsubscribe from notification:", error);
        notify({
          type: "error",
          text: "Értesítés kikapcsolás nem sikerült!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
  }
})
