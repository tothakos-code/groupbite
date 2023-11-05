import { state, socket } from "@/socket.js";
import { computed } from "vue";

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
    socket.emit("User Login", {"username": username}, function(user) {
      state.user = user;
    });
  }

  return {
    isLoggedIn,
    userColor,
    matchUiColorWithBuiltIn,
    login
  }
}
export function userColorF(){
  const userColor = computed(() => {
    return state.user.ui_color ? state.user.ui_color : "falusi";
  });
  return {
    userColor
  };
}
