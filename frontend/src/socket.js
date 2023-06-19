import { reactive } from "vue";
import { io } from "socket.io-client";

export const state = reactive({
  connected: false,
  orderState: '',
  globalBasket: {}
});

// "undefined" means the URL will be computed from the `window.location` object
// const URL = process.env.NODE_ENV === "production" ? undefined : "http://localhost:3000";
const URL = undefined;

export const socket = io(URL);


socket.on("connect", () => {
  console.log('VUE Socket.IO connection established VUE');
  state.connected = true;
  socket.emit('Request order state', function(incomingState) {
    console.log("VUE Recived ORDER data from return VUE:" + incomingState);
    state.orderState = incomingState;
  });
});

socket.on("disconnect", () => {
  state.connected = false;
});

socket.on('Order state changed', function(incomingState) {
  console.log("VUE Order update incoming VUE:" + incomingState);
  state.orderState = incomingState;
});

socket.on('Client Basket Update', function(incomingGlobalBasket) {
  console.log('VUE Global basket incomming via websocket VUE: ', incomingGlobalBasket);
  state.globalBasket = incomingGlobalBasket.basket;
});
