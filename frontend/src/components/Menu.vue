<template>
  <div class="card">
    <div class="card-header row d-flex">
      <div class="col-6">
        <h2 class="ps-0">Étlap</h2>
      </div>
      <div class="col-6">
        <Datestamp @selectedDate="(day) => this.getMenu(day)" :limitToCurrentWeek="true"/>
      </div>
    </div>
    <div class="row">
      <div class="col">
        <div class="list-group">
          <div
            v-for="item in items"
            :key="item.id"
            class="list-group-item row d-flex">
            <div class="col-8">
              <span>
                {{ item.label }}
              </span>
            </div>
            <div class="col-4">
              <div class="d-flex justify-content-end">
                <span v-if="item.sold_out" class="btn pe-none btn-outline-danger">Elfogyott</span>
                <button
                  v-else
                  v-for="size in item.sizes"
                  :key="item.id-size.size"
                  @click="addToBasket(item.id, item.label, size.size, size.price, size.link)"
                  class="btn btn-sm col-sm-6 me-2 ms-2"
                  :class="['btn-' + this.usercolor ]">
                  {{ size.label }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useCookies } from "vue3-cookies";
import Datestamp from './DateStamp.vue'
import { state, socket } from "@/socket";


export default {
  name: 'FalusiMenu',
  components: {
    Datestamp
  },
  setup() {
    const { cookies } = useCookies();
    return { cookies };
  },
  mounted() {
    this.getMenu();
  },
  methods: {
    addToBasket: function(fid, label, size, price, link) {
      if (state.user.username === undefined) {
        alert("Jelentkezz be a rendeléshez");
        return;
      }
      if (state.orderState === 'closed') {
        alert("A rendelés már ellett küldve. Már nem módisíthatsz a kosaradon");
        return;
      }
      if (this.currentUserState === 'skip') {
        socket.emit("User Daily State Change",{ 'username': state.user.username, 'new_state':'none' });
      }
      const itemSizeKey = fid + '-' + size;
      if (state.localBasket[itemSizeKey]) {
        // If the item already exists in the basket, increment the quantity
        state.localBasket[itemSizeKey].quantity += 1;
      } else {
        // Otherwise, add a new entry to the basket
        state.localBasket[itemSizeKey] = {
          id: fid,
          name: label,
          size: size,
          price: price,
          link: link,
          quantity: 1
        };
      }
    },
    getMenu: function(day) {
      let url = ''
      if (day === undefined) {
        url = `http://${window.location.hostname}/api/menu/get`
      } else {
        url = `http://${window.location.hostname}/api/menu/get/${new Date(day).toISOString().split('T')[0]}`
      }

      fetch(url)
        .then(response => response.json())
          .then(data => {
            this.items = data;
            console.log(this.items);
          })
        .catch(error => console.error(error));
    }
  },
  data() {
    return {
      items: []
    }
  },
  computed: {
    currentUserState() {
      return state.userStates[state.user.username];
    },
    usercolor() {
        return state.user.ui_color ? state.user.ui_color : "falusi";
    }
  }
}
</script>

<style>
[data-bs-theme=light] .list-group-item:hover {
  background-color: lightgray;
}
[data-bs-theme=dark] .list-group-item:hover {
  background-color: #3c3c3c;
}
</style>
