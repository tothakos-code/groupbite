import axios from 'axios';
import Cookies from 'js-cookie';
import { defineStore } from 'pinia'

export const useAuth = defineStore('user', {
  state: () => ({ user: null, isLoggedIn: false, isLoading: true}),
  getters: {
    getUserColor() {
      // TODO: implement user setings, this is not excist yet
      // if (state.isLoggedIn) {
      //   return this.auth.user.ui_color;
      // }
      return "falusi"
    },
  },
  actions: {
    async login(user_id) {
      try {
        const response = await axios.post(
          `http://${window.location.host}/api/user/login`, {
            "user": user_id
        });

        this.user = response.data
        Cookies.set("user", this.user.id, { expires: 365});
        this.isLoading = false;
        this.isLoggedIn = true;
      } catch (error) {
        console.log("Error during login:" + error);
        this.isLoading = false;

      }
    },
    async register(username) {
      try {
        const response = await axios.post(
          `http://${window.location.host}/api/user/register`, {
            "username": username
          })
        this.user_obj = response.data
        Cookies.set("user", this.user.id, { expires: 365});
        this.isLoading = false;
        this.isLoggedIn = true;
      } catch (error) {
        console.log("Error during login:" + error);
        this.isLoading = false;

      }
    },
    checkSession() {
      let session = Cookies.get('user')
      console.log(session);
      if (session) {
        this.login(session)
      } else {
        this.isLoading = false;
      }
    }
  }
})
