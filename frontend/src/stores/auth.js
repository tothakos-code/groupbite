import axios from 'axios';
import Cookies from 'js-cookie';
import { defineStore } from 'pinia'
import { notify } from "@kyvg/vue3-notification";


export const useAuth = defineStore('user', {
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
        const response = await axios.post(
          `http://${window.location.host}/api/user/login`, {
            "username": username
        });
        if (response.data.error) {
          notify({
            type: "warn",
            text: response.data.error,
          });
          return;
        }

        this.user = response.data;
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
    async register(username) {
      try {
        const response = await axios.post(
          `http://${window.location.host}/api/user/register`, {
            "username": username
          });
        if (response.data.error) {
          notify({
            type: "warn",
            text: response.data.error,
          });
          return;
        }
        this.user = response.data
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
      let session = Cookies.get('user')
      if (session) {
        try {
          const response = await axios.post(
            `http://${window.location.host}/api/user/checkSession`, {
              "session": session
          });
          if (response.data.error) {
            return;
          }

          this.user = response.data;
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
    }
  }
})
