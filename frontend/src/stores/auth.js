import axios from "axios";
import { defineStore } from "pinia"
import { notify } from "@kyvg/vue3-notification";


export const useAuth = defineStore("user", {
  state: () => ({ user: null, isLoggedIn: false, isLoading: true}),
  getters: {
    getUserColor() {
      // TODO: implement user setings, this is not excist yet
      // if (state.isLoggedIn) {
      //   return this.auth.user.ui_color;
      // }
      return "primary"
    },
  },
  actions: {
    async login(username) {
      try {
        const response = await axios.post(`/api/user/login`, {
            "username": username
        });
        if (response.data.error) {
          notify({
            type: "warn",
            text: response.data.error,
          });
          return response;
        }

        this.user = response.data.data;
        this.isLoading = false;
        this.isLoggedIn = true;
        notify({
          type: "info",
          text: "Sikeresen bejelentkeztél.",
        });
        return response
      } catch (error) {
        console.log("Error during login:" + error);
        this.isLoading = false;
        return error.response

      }
    },
    async logout() {
      try {
        const response = await axios.post(`/api/user/logout`);
        if (response.data.error) {
          notify({
            type: "warn",
            text: response.data.error,
          });
          return;
        }

        this.user = null;
        this.isLoggedIn = false;
        notify({
          type: "info",
          text: "Sikeresen kijelentkeztél.",
        });
      } catch (error) {
        console.log("Error during logout:" + error);
        this.isLoading = false;

      }
    },
    async register(username, email) {
      try {
        const response = await axios.post(`/api/user/register`, {
            "username": username,
            "email": email
          });
        if (response.data.error) {
          notify({
            type: "warn",
            text: response.data.error,
          });
          return;
        }
        this.user = response.data.data
        notify({
          type: "info",
          text: "Felhasználói fiók létrehozva és bejelentkeztetve.",
        });
        this.isLoading = false;
        this.isLoggedIn = true;
      } catch (error) {
        console.log("Error during login:" + error);
        this.isLoading = false;

      }
    },
    async checkSession() {
      try {
        const response = await axios.get(`/api/user/checkSession`);
        if (response.data.error) {
          console.log(response.data.error);
          return;
        }

        this.user = response.data.data;
        this.isLoading = false;
        this.isLoggedIn = true;
      } catch (error) {
        console.log("Error during session check:" + error);
        this.isLoading = false;

      }
    },
    async sendReminder(email) {
      try {
        const response = await axios.get(`/api/user/reminder`,
          { "params": {"email": email} }
        );
        if (response.data.error) {
          notify({
            type: "warn",
            text: response.data.error,
          });
          return;
        }
        notify({
          type: "info",
          text: "Emlékeztető email kiküldve!",
        });
        this.isLoading = false;
      } catch (error) {
        console.log("Error during reminder send:" + error);
        this.isLoading = false;

      }
    },
    async orders(querryParams) {
      this.isLoading = true;
      try {
        const response = await axios.get(`/api/user/${this.user.id}/orders`,
          { "params": querryParams }
        );
        return response
      } catch (error) {
        console.error("Failed to get orders", error);
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async fetchAll(querryParams) {
      this.isLoading = true;
      try {
        const response = await axios.get(`/api/user/`, { "params": querryParams });
        return response
      } catch (error) {
        console.error("Failed to get users:", error.response.data.error);
        return error.response
      } finally {
        this.isLoading = false;
      }
    },
    async update(data) {
      this.isLoading = true;
      try {
        const response = await axios.put(`/api/user/${this.user.id}`, { "data": data });
        return response
      } catch (error) {
        console.error("Failed to update user", error);
        notify({
          type: "warn",
          text: error.response.data.error,
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    }
  }
})
