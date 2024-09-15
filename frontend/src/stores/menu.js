import axios from "axios";
import { defineStore } from "pinia"
import { notify } from "@kyvg/vue3-notification";

export const useMenuStore = defineStore("menu", {
  state: () => ({
    menu: {},
    isLoading: false
  }),
  getters: {
    getItems: (state) => {
      return state.menu.items
    }
  },
  actions: {
    async fetch(menuId) {
      this.isLoading = true;
      try {
        const response = await axios.get(`/api/menu/${menuId}`);
        return response
      } catch (error) {
        console.error("Failed to fetch menu by ID:", error.response.data.error);
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async update(menuId, data) {
      this.isLoading = true;
      try {
        const response = await axios.put(`/api/menu/${menuId}`, { "data": data });
        notify({
          type: "info",
          text: "Menü frissítés sikeres!",
        });
        return response
      } catch (error) {
        console.error("Failed to update menu:", error.response.data.error);
        notify({
          type: "error",
          text: "Menü frissítés nem sikerült!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async delete(menuId) {
      this.isLoading = true;
      try {
        const response = await axios.delete(`/api/menu/${menuId}`);
        notify({
          type: "info",
          text: "Menü törlés sikeres!",
        });
        return response
      } catch (error) {
        console.error("Failed to delete menu:",  error.response.data.error);
        notify({
          type: "error",
          text: "Menü törlés nem sikerült!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async duplicate(menuId, data) {
      this.isLoading = true;
      try {
        const response = await axios.post(`/api/menu/${menuId}/duplicate`, { "data": data });
        notify({
          type: "info",
          text: "Menü duplikálva!",
        });
        return response
      } catch (error) {
        console.error("Failed to duplicate menu:", error.response.data.error);
        notify({
          type: "error",
          text: "Menü duplikáció nem sikerült!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async add(data) {
      this.isLoading = true;
      try {
        const response = await axios.post(`/api/menu`, { "data": data });
        notify({
          type: "info",
          text: "Menü hozzáadása sikeres!",
        });
        return response

      } catch (error) {
        console.error("Failed to add menu:", error.response.data.error);
        notify({
          type: "error",
          text: "Menü hozzáadása nem sikerült!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async activate(menuId) {
      this.isLoading = true;
      try {
        const response = await axios.get(`/api/menu/${menuId}/activate`);
        notify({
          type: "info",
          text: "Menü aktiválás sikeres!",
        });
        return response
      } catch (error) {
        console.error("Failed to activate menu:", error.response.data.error);
        notify({
          type: "error",
          text: "Menü aktiválás sikertelen!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async deactivate(menuId) {
      this.isLoading = true;
      try {
        const response = await axios.get(`/api/menu/${menuId}/deactivate`);
        notify({
          type: "info",
          text: "Menü deaktiválás sikeres!",
        });
        return response
      } catch (error) {
        console.error("Failed to deactivate menu:", error.response.data.error);
        notify({
          type: "error",
          text: "Menü deaktiválás sikertelen!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
  }
})
