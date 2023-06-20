<template>
  <div class="card">
    <div class="card-header row d-flex">
      <div class="col-6">
        <h2 class="ps-0">Étlap</h2>
      </div>
      <div class="col-6">
        <Datestamp @selectedDate="(day) => this.getMenu(day)"/>
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
                <button
                  v-for="size in item.sizes"
                  :key="item.id-size.size"
                  @click="addToBasket(item.id, item.label, size.size, size.price, size.link)"
                  class="btn btn-warning btn-sm col-sm-6 me-2 ms-2">
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
import { state } from "@/socket";


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
  emits: ['basketUpdate'],
  methods: {
    addToBasket: function(fid, label, size, price, link) {
      if (state.orderState === 'closed') {
        alert("A rendelés már ellett küldve. Már nem módisíthatsz a kosaradon");
        return;
      }
      let basket = this.cookies.get('basket') || {};
      const itemSizeKey = fid + '-' + size;
      if (basket[itemSizeKey]) {
        // If the item already exists in the basket, increment the quantity
        basket[itemSizeKey].quantity += 1;
      } else {
        // Otherwise, add a new entry to the basket
        basket[itemSizeKey] = {
          id: fid,
          name: label,
          size: size,
          price: price,
          link: link,
          quantity: 1
        };
      }
      this.cookies.set('basket',basket,'16h');
      this.$emit('basketUpdate');
    },
    getMenu: function(day) {
      fetch(`http://${window.location.hostname}/api/getmenu?day=${day}`)
        .then(response => response.json())
          .then(data => {
            this.items = data;
          })
        .catch(error => console.error(error));
    }
  },
  data() {
    return {
      items: []
    }
  }
}
</script>

<style>
</style>
