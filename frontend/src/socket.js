import { reactive } from "vue";
import { io } from "socket.io-client";

export const state = reactive({
  connected: false,
  orderState: '',
  globalBasket: {},
  localBasket: {},
  user: {},
  userStates: {}
});

// "undefined" means the URL will be computed from the `window.location` object
// const URL = process.env.NODE_ENV === "production" ? undefined : "http://localhost:3000";
const URL = undefined;

export const socket = io(URL);


socket.on("connect", () => {
  console.log('VUE Socket.IO connection established VUE');
  state.connected = true;
  fetch(`http://${window.location.hostname}/api/order/get-order-state`)
    .then(response => response.json())
      .then(data => {
        state.orderState = data.order_state;
      })
    .catch(error => console.error(error));
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

socket.on('Waiting Update', function(incomingStateList) {
  state.userStates = incomingStateList;
});

socket.on('Refresh!', function() {
  console.log("Refresh");
  location.reload();
});
