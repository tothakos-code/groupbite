import axios from "axios";
import Cookies from "js-cookie";
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
      const theme  = localStorage.getItem("theme")
      if (theme === "light") {
        return "groupbite"
      } else {
        return "groupbite-dark"
      }
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
          return;
        }

        this.user = response.data.data;
        Cookies.set("user", this.user.id, { expires: 365});
        this.isLoading = false;
        this.isLoggedIn = true;
        notify({
          type: "info",
          text: "Sikeresen bejelentkeztél.",
        });
      } catch (error) {
        console.log("Error during login:" + error);
        this.isLoading = false;

      }
    },
    logout() {
      this.user = null;
      this.isLoggedIn = false;
      Cookies.remove("user");
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
        Cookies.set("user", this.user.id, { expires: 365});
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
      let session = Cookies.get("user")
      if (session) {
        try {
          const response = await axios.post(`/api/user/checkSession`, {
              "session": session
          });
          if (response.data.error) {
            return;
          }

          this.user = response.data.data;
          Cookies.set("user", this.user.id, { expires: 365});
          this.isLoading = false;
          this.isLoggedIn = true;
        } catch (error) {
          console.log("Error during session check:" + error);
          this.isLoading = false;

        }
      } else {
        this.isLoading = false;
      }
    },
    async orders() {
      this.isLoading = true;
      try {
        const response = await axios.get(`/api/user/${this.user.id}/orders`);
        return response
      } catch (error) {
        console.error("Failed to get orders", error);
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
        console.error("Failed to get orders", error);
        notify({
          type: "warn",
          text: error.response.error,
        });
        return error.response
      } finally {
        this.isLoading = false;
      }
    }
  }
})
