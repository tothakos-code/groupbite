import 'setimmediate'
import { reactive } from "vue";
import { io } from "socket.io-client";
import router from './router.js';
import { register_plugin_routes } from './loader.js';
import { useBasket } from '@/stores/basket'
// import { useVendor } from '@/stores/vendor'

export const state = reactive({
  connected: false,
  order: {},
  selectedDate: new Date(), // TODO: This will be urlencoded
  vendors: [],
  selected_vendor: undefined,
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

socket.on('be_vendors_update', function(vendors) {
  state.vendors = JSON.parse(vendors);
  // const vendor = useVendor();
  // vendor.vendors = JSON.parse(vendors)
  // state.vendors.forEach((item) => {
  //   item.component = import("@/../../plugins/"+item.name+"/frontend/App.vue");
  // });
  register_plugin_routes(router);
});

socket.on('be_order_update', function(data) {
  const basket = useBasket();
  if (data.basket) {
    basket.basket = data.basket;
  }
  console.log(data.basket);
  if (data.order) {
    state.order = data.order;
  }
});

socket.on('Refresh!', function() {
  console.log("Refresh");
  location.reload();
});

export function change_selected_date(new_date) {
  socket.emit("fe_date_selection", {
    "old_selected_date": state.selectedDate.toISODate(),
    "new_selected_date": new_date.toISODate(),
    "vendor_id": state.selected_vendor
  })
  state.selectedDate = new_date;
}
