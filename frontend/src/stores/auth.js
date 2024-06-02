import axios from 'axios';
import Cookies from 'js-cookie';
import { defineStore } from 'pinia'

export const useAuth = defineStore('user', {
  state: () => ({ user_obj: null, loggedIn: false, authChecked: false}),
  getters: {
    user(state) {
      return state.user_obj;
    },
    isLoggedIn(state) {
      return state.loggedIn;
    },
    isAuthChecked(state) {
      return state.authChecked;
    },
    getUserColor() {
      // TODO: implement user setings, this is not excist yet
      // if (state.loggedIn) {
      //   return this.auth.user.ui_color;
      // }
      return "falusi"
    },
  },
  actions: {
    async login(username) {
      console.log(username);
      try {
        const response = await axios.post(
          `http://${window.location.host}/api/user/login`, {
            "username": username
          })
        this.user_obj = response.data
        console.log(this.user_obj);
        this.authChecked = true;
        this.loggedIn = true;
        Cookies.set("username", this.user.username, { expires: 365});
      } catch (error) {
        console.log("Error during login:" + error);
        this.authChecked = true;

      }
    },
    checkSession() {
      let session = Cookies.get('username')
      console.log(session);
      if (session) {
        this.login(session)
      } else {
        this.authChecked = true;
      }
    }
  }
})
