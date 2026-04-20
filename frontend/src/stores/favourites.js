import axios from "axios";
import { defineStore } from "pinia";
import { notify } from "@kyvg/vue3-notification";
import { regWorker } from "@/main";

export const useFavouritesStore = defineStore("favourites", {
  state: () => ({
    favourites: [],
    // {menu_item_id: favourite_id} — set after fetchMatches
    matchedItemIds: {},
    isLoading: false,
  }),
  actions: {
    async fetchFavourites(vendorId) {
      this.isLoading = true;
      try {
        const response = await axios.get(`/api/vendor/${vendorId}/favourites`);
        this.favourites = response.data.data;
        return response;
      } catch (error) {
        console.error("Failed to fetch favourites:", error);
        return error.response;
      } finally {
        this.isLoading = false;
      }
    },

    async fetchAllFavourites() {
      try {
        const response = await axios.get(`/api/user/favourites`);
        return response.data.data || [];
      } catch (error) {
        console.error("Failed to fetch all favourites:", error);
        return [];
      }
    },

    async addFavourite(vendorId, itemName) {
      try {
        const response = await axios.post(`/api/vendor/${vendorId}/favourites`, {
          item_name: itemName,
        });
        if (response.data.data) {
          const exists = this.favourites.find((f) => f.id === response.data.data.id);
          if (!exists) {
            this.favourites.push(response.data.data);
          }
        }
        return response;
      } catch (error) {
        console.error("Failed to add favourite:", error);
        notify({ type: "error", text: "Kedvenc hozzáadása nem sikerült!" });
        return error.response;
      }
    },

    async removeFavourite(vendorId, favouriteId) {
      try {
        const response = await axios.delete(
          `/api/vendor/${vendorId}/favourites/${favouriteId}`
        );
        this.favourites = this.favourites.filter((f) => f.id !== favouriteId);
        // reassign to trigger Vue reactivity — delete on a reactive object is not detected
        const updated = { ...this.matchedItemIds };
        for (const [itemId, favId] of Object.entries(updated)) {
          if (favId === favouriteId) delete updated[itemId];
        }
        this.matchedItemIds = updated;
        return response;
      } catch (error) {
        console.error("Failed to remove favourite:", error);
        notify({ type: "error", text: "Kedvenc törlése nem sikerült!" });
        return error.response;
      }
    },

    async fetchMatches(vendorId, menuDate) {
      try {
        const params = menuDate ? { date: menuDate } : {};
        const response = await axios.get(
          `/api/vendor/${vendorId}/favourites/matches`,
          { params }
        );
        this.matchedItemIds = response.data.data || {};
        return response;
      } catch (error) {
        console.error("Failed to fetch favourite matches:", error);
        return error.response;
      }
    },

    isMatched(itemId) {
      return Object.prototype.hasOwnProperty.call(this.matchedItemIds, itemId);
    },

    getMatchedFavouriteId(itemId) {
      return this.matchedItemIds[itemId] ?? null;
    },

    async ensureFavouriteNotificationsEnabled(vendorId) {
      if (!('Notification' in window) || !('serviceWorker' in navigator) || !('PushManager' in window)) return;

      // Get current push subscription endpoint to check device-level status
      let endpoint = null;
      try {
        const reg = await navigator.serviceWorker.getRegistration('/');
        const sub = reg ? await reg.pushManager.getSubscription() : null;
        endpoint = sub ? sub.endpoint : null;
      } catch { /* ignore */ }

      // Check if this device is already subscribed for favourite notifications
      try {
        const params = endpoint ? { endpoint } : {};
        const response = await axios.get(`/api/vendor/${vendorId}/notifications/favourite`, { params });
        const status = response.data.data ?? {};
        if (status.device_subscribed) return; // already enabled on this device
      } catch { /* ignore, proceed to subscribe */ }

      // Request browser permission if not yet granted
      if (Notification.permission === 'denied') {
        notify({ type: "warn", text: "Az értesítések blokkolva vannak. Engedélyezd a böngésző beállításaiban a kedvenc értesítésekhez." });
        return;
      }
      if (Notification.permission === 'default') {
        const permission = await Notification.requestPermission();
        if (permission !== 'granted') return;
      }

      // Subscribe and register with the backend
      try {
        await regWorker();
        const publicKey = await axios.get("/vapid_public_key");
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: publicKey.data,
        });
        await axios.post(`/api/vendor/${vendorId}/notifications/favourite/subscribe`, {
          data: subscription,
        });
        notify({ type: "info", text: "Kedvenc értesítések bekapcsolva!" });
      } catch (error) {
        console.error("Failed to subscribe to favourite notifications:", error);
        notify({ type: "error", text: "Kedvenc értesítés beállítása nem sikerült!" });
      }
    },
  },
});
