import { reactive } from "vue";
import { io } from "socket.io-client";

export const state = reactive({
  connected: false,
  orderState: ''
});

// "undefined" means the URL will be computed from the `window.location` object
// const URL = process.env.NODE_ENV === "production" ? undefined : "http://localhost:3000";
const URL = undefined;

export const socket = io(URL);


socket.on("connect", () => {
  console.log('VUE Socket.IO connection established VUE');
  state.connected = true;
});

socket.on("disconnect", () => {
  state.connected = false;
});

