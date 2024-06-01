<template>
  <div class="list-group-item row d-flex ">
    <div class="col-12 col-lg-8 p-0">
      <span>
        {{ item.name }}
      </span>
    </div>
    <div class="col-12 col-lg-4 p-0 flex-wrap">
      <div class="d-flex justify-content-end">
        <!-- <span
          v-if="item.sold_out"
          class="btn pe-none btn-outline-danger btn-sm"
        >Elfogyott</span> -->
        <button
          v-for="size in item.sizes"
          :key="size.id"
          class="btn btn-sm col-6 col-sm-6 ms-2"
          :class="['btn-' + auth.getUserColor ]"
          @click="addToBasket(size.id, size.size)"
        >
          <span class="text-nowrap me-1">{{ size.size }}</span>
          <span class="text-nowrap">{{ size.price }} Ft</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { state, socket } from "@/socket";
import { useAuth } from "@/auth";
import { notify } from "@kyvg/vue3-notification";
import axios from 'axios';

export default {
  name: 'FalusiMenu',
  props: {
    'item':{
      type: Object,
      default: new Object()
    },
  },
  setup() {
    const auth = useAuth();
    return {
      auth
    }
  },
  computed: {
    currentUserState() {
      return state.userStates[this.auth.user.username];
    }
  },
  methods: {
    addToBasket: function(mi_id) {
      if (!this.auth.isLoggedIn.value) {
        notify({
          type: "warn",
          text: "Jelentkezz be a rendeléshez!",
        });
        return;
      }
      if (state.order.state_id === 'closed') {
        notify({
          type: "warn",
          text: "A rendelés már el lett küldve. Már nem módosíthatod a kosaradat.",
        });
        return;
      }
      if (this.currentUserState === 'skip') {
        socket.emit("User Daily State Change",{ 'id': this.auth.user.id, 'new_state':'none' });
      }
      axios.post(`http://${window.location.host}/api/order/${state.order.id}/add`,{
        "user_id":this.auth.user.id,
        "menu_item_id":mi_id
      })
    }
  }
}
</script>

<style>
</style>
