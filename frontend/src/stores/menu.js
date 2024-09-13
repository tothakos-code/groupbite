import axios from "axios";
import { defineStore } from "pinia"
import { notify } from "@kyvg/vue3-notification";

export const useMenu = defineStore("menu", {
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
        const response = await axios.get(`/api/menu/${menuId}/fetch`);
        return response
      } catch (error) {
        console.error("Failed to fetch menu by ID",error);
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async update(menu, data) {
      this.isLoading = true;
      try {
        const response = await axios.post(`/api/menu/${menu}/update`, data);
        notify({
          type: "info",
          text: "Menü frissítés sikeres!",
        });
        return response
      } catch (error) {
        console.error("Failed to update menu",error);
        notify({
          type: "error",
          text: "Menü frissítés nem sikerült!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async delete(menu, data) {
      this.isLoading = true;
      try {
        const response = await axios.post(`/api/menu/${menu}/delete`, data);
        notify({
          type: "info",
          text: "Menü törlés sikeres!",
        });
        return response
      } catch (error) {
        console.error("Failed to delete menu",error);
        notify({
          type: "error",
          text: "Menü törlés nem sikerült!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async duplicate(menu, data) {
      this.isLoading = true;
      try {
        const response = await axios.post(`/api/menu/${menu}/duplicate`, data);
        notify({
          type: "info",
          text: "Menü duplikálva!",
        });
        return response
      } catch (error) {
        console.error("Failed to duplicate menu",error);
        notify({
          type: "error",
          text: "Menü duplikáció nem sikerült!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async add(menu, data) {
      this.isLoading = true;
      try {
        const response = await axios.post(`/api/menu/${menu}/add`, data);
        notify({
          type: "info",
          text: "Menü hozzáadása sikeres!",
        });
        return response

      } catch (error) {
        console.error("Failed to add menu",error);
        notify({
          type: "error",
          text: "Menü hozzáadása nem sikerült!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async activate(menu) {
      this.isLoading = true;
      try {
        const response = await axios.get(`/api/menu/${menu}/activate`);
        notify({
          type: "info",
          text: "Menü aktiválás sikeres!",
        });
        return response
      } catch (error) {
        console.error("Failed to activate menu",error);
        notify({
          type: "error",
          text: "Menü aktiválás sikertelen!",
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async deactivate(menu) {
      this.isLoading = true;
      try {
        const response = await axios.get(`/api/menu/${menu}/deactivate`);
        notify({
          type: "info",
          text: "Menü deaktiválás sikeres!",
        });
        return response
      } catch (error) {
        console.error("Failed to deactivate menu",error);
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
