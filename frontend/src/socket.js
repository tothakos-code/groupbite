import { reactive } from "vue";
import { io } from "socket.io-client";
import router from './router.js';
import { register_plugin_routes } from './loader.js';

export const state = reactive({
  connected: false,
  orderState: '', // TODO: This will be removed
  order: {},
  basket: {},
  globalBasket: {}, // TODO: This will be removed
  userBasket: [],
  selectedDate: new Date(), // TODO: This will be urlencoded
  user: {},
  vendors: [],
  userStates: {} // TODO: Something will need to happen to this. currently unclear
});

// "undefined" means the URL will be computed from the `window.location` object
// const URL = process.env.NODE_ENV === "production" ? undefined : "http://localhost:3000";
const URL = undefined;

export const socket = io(URL);


socket.on("connect", () => {
  state.connected = true;
});

socket.on("disconnect", () => {
  state.connected = false;
});

socket.on('Order state changed', function(incomingState) {
  state.orderState = incomingState;
});

socket.on('be_vendors_update', function(vendors) {
  state.vendors = JSON.parse(vendors);
  console.log(state.vendors);
  state.vendors.forEach((item) => {
    item.component = import("@/../../plugins/"+item.name+"/frontend/App.vue");
  });
  register_plugin_routes(router);
  console.log(state.vendors);
});

socket.on('Client Basket Update', function(incomingGlobalBasket) {
  state.basket = JSON.parse(incomingGlobalBasket);
  if (state.user.username !== undefined) {
    state.userBasket = [];
    for (const item of state.basket) {
      if (item['username'] === state.user.username) {
        state.userBasket.push(item);
      }
    }

  }
});

socket.on('Waiting Update', function(incomingStateList) {
  state.userStates = incomingStateList;
});

socket.on('Refresh!', function() {
  console.log("Refresh");
  location.reload();
});
