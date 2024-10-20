import "setimmediate"
import { reactive } from "vue";
import { io } from "socket.io-client";
import router from "./router.js";
import { register_plugin_routes } from "./loader.js";
import { useOrderStore } from "@/stores/order"
import { useVendorStore } from "@/stores/vendor"
import { useAuth } from "@/stores/auth"

export const state = reactive({
  connected: false,
  selectedDate: new Date(), // TODO: This will be urlencoded
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

socket.on("be_vendors_update", function(vendors) {
  useVendorStore().vendors = JSON.parse(vendors);
  register_plugin_routes(router);
});

socket.on("be_user_update", function(user) {
  useAuth().user = user;
});

socket.on("be_order_update", function(data) {
  const order = useOrderStore();
  if (data.basket) {
    order.basket = data.basket;
  }
  if (data.order) {
    order.order = data.order;
  }
});

socket.on("Refresh!", function() {
  console.log("Refresh");
  location.reload();
});
