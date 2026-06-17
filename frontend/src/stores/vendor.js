import axios from "axios";
import { defineStore } from "pinia"
import { notify } from "@kyvg/vue3-notification";
import { regWorker } from "@/main";
import { useAuth } from "@/stores/auth";
import i18n from "@/plugins/i18n";

export const useVendorStore = defineStore("vendor", {
  state: () => ({
    vendors: [],
    selectedVendor: undefined,
    isLoading: false,
    routesLoaded: false
  }),
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
    async fetchMenus(vendorId, queryParams) {
      this.isLoading = true;
      try {
        const response = await axios.get(`/api/vendor/${vendorId}/menus`,
          { "params": queryParams }
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
        console.error("Failed to add vendor:", error.response?.data?.error);
        const errorKey = error.response?.data?.error || ''
        const knownKeys = ['name_taken', 'unknown_plugin']
        const msgKey = knownKeys.includes(errorKey) ? `vendor.errors.${errorKey}` : 'vendor.errors.default'
        notify({
          type: "error",
          text: i18n.global.t(msgKey),
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
    async fetchVendorSettings(vendorId) {
      this.isLoading = true;
      try {
        const response = await axios.get(`/api/vendor/${vendorId}/settings`);
        return response
      } catch (error) {
        console.error("Failed to get vendor settings:", error.response.data.error);
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async fetchWebhooks(vendorId) {
      this.isLoading = true;
      try {
        const response = await axios.get(`/api/vendor/${vendorId}/webhooks`);
        return response
      } catch (error) {
        console.error("Failed to get vendor webhooks:", error.response.data.error);
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
    async fetchPlugins() {
      try {
        const response = await axios.get('/api/plugins');
        return response;
      } catch (error) {
        console.error('Failed to fetch plugins:', error.response?.data?.error);
        return error.response;
      }
    },
    async fetchPluginSettings(vendorId) {
      try {
        const response = await axios.get(`/api/vendor/${vendorId}/plugin-settings`);
        return response;
      } catch (error) {
        return error.response;
      }
    },
    async savePluginSettings(vendorId, data) {
      this.isLoading = true;
      try {
        const response = await axios.put(`/api/vendor/${vendorId}/plugin-settings`, { data });
        notify({ type: 'info', text: 'Plugin beállítások mentése sikeres!' });
        return response;
      } catch (error) {
        console.error('Failed to save plugin settings:', error.response?.data?.error);
        notify({ type: 'error', text: 'Plugin beállítások mentése nem sikerült!' });
        return error.response;
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
        // Permission is already granted by the UI layer before calling this action.
        // Just ensure the service worker is registered.
        await regWorker();

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
        // Also unsubscribe from the browser push manager
        try {
          const reg = await navigator.serviceWorker.getRegistration('/');
          if (reg) {
            const sub = await reg.pushManager.getSubscription();
            if (sub) await sub.unsubscribe();
          }
        } catch (e) { /* ignore, server-side unsubscribe still proceeds */ }

        const response = await axios.delete(`/api/vendor/${this.selectedVendor.id}/notifications/reminder/unsubscribe`)
        notify({
          type: "info",
          text: `Kikapcsoltad a(z) ${this.selectedVendor.name} értesítést minden eszközön!`,
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
    async unsubscribeDevice(endpoint) {
      const auth = useAuth()
      if (!auth.isLoggedIn) return;
      try {
        // Unsubscribe from browser push manager if it matches this device
        try {
          const reg = await navigator.serviceWorker.getRegistration('/');
          if (reg) {
            const sub = await reg.pushManager.getSubscription();
            if (sub && sub.endpoint === endpoint) await sub.unsubscribe();
          }
        } catch (e) { /* ignore */ }

        await axios.delete(
          `/api/vendor/${this.selectedVendor.id}/notifications/reminder/unsubscribe/device`,
          { data: { endpoint } }
        );
        notify({
          type: "info",
          text: `Kikapcsoltad a(z) ${this.selectedVendor.name} értesítést ezen az eszközön!`,
        });
      } catch (error) {
        console.error("Failed to unsubscribe device from notification:", error);
        notify({
          type: "error",
          text: "Értesítés kikapcsolás nem sikerült!",
        });
      } finally {
        this.isLoading = false;
      }
    },
  }
})
