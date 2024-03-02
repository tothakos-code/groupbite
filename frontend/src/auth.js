import { state } from "@/socket.js";
import { computed } from "vue";
import axios from 'axios';

export function useAuth() {

  const isLoggedIn = computed(() => {
    return state.user.id !== undefined;
  });
  const userColor = computed(() => {
    return state.user.ui_color ? state.user.ui_color : "falusi";
  });

  const matchUiColorWithBuiltIn = computed(() => {
    switch (state.user.ui_color ? state.user.ui_color : "falusi") {
      case "steelblue":
        return "info";
      case "raspberry":
        return "danger";
      case "tigragold":
        return "warning";
      default:
        // falusi
        return "warning"
    }
  });

  function login(username) {
    axios.post(
      `http://${window.location.host}/api/user/login`, {
        "username": username
    })
    .then(function(response) {
      state.user = response.data;
      console.log(state.user);
    })
    .catch(function (error) {
      console.log("Error during login:" + error);
    });
  }

  return {
    isLoggedIn,
    userColor,
    matchUiColorWithBuiltIn,
    login
  }
}
