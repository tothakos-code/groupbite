<template>
  <div class="card">
    <div class="card-header row d-flex justify-content-between p-1">
      <div class="col-2 col-lg-1 my-auto">
          <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="currentColor" class="bi bi-basket2 mb-1" viewBox="0 0 16 16">
            <path d="M4 10a1 1 0 0 1 2 0v2a1 1 0 0 1-2 0v-2zm3 0a1 1 0 0 1 2 0v2a1 1 0 0 1-2 0v-2zm3 0a1 1 0 1 1 2 0v2a1 1 0 0 1-2 0v-2z"/>
            <path d="M5.757 1.071a.5.5 0 0 1 .172.686L3.383 6h9.234L10.07 1.757a.5.5 0 1 1 .858-.514L13.783 6H15.5a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-.623l-1.844 6.456a.75.75 0 0 1-.722.544H3.69a.75.75 0 0 1-.722-.544L1.123 8H.5a.5.5 0 0 1-.5-.5v-1A.5.5 0 0 1 .5 6h1.717L5.07 1.243a.5.5 0 0 1 .686-.172zM2.163 8l1.714 6h8.246l1.714-6H2.163z"/>
          </svg>
      </div>
      <div class="col-3 col-lg-4 d-none d-sm-inline d-md-none d-lg-inline text-start my-auto">
        <h2 class="text-nowrap">Kosarad</h2>
      </div>
      <div class="col-7 col-sm-3 col-md-7 col-lg-5 text-center m-auto">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-cash me-1 mb-1" viewBox="0 0 16 16">
          <path d="M8 10a2 2 0 1 0 0-4 2 2 0 0 0 0 4z"/>
          <path d="M0 4a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H1a1 1 0 0 1-1-1V4zm3 0a2 2 0 0 1-2 2v4a2 2 0 0 1 2 2h10a2 2 0 0 1 2-2V6a2 2 0 0 1-2-2H3z"/>
        </svg>
        <span title="A fizetendő összeg még változhat, a rendelést leadó személyek számától.(Szállítási díjat több fele osztjuk)">{{ sumBasket }} Ft</span>
      </div>
      <div class="col-3 col-lg-2 text-end my-auto">
        <button title="Kosarad ürítése" class="btn" :class="['btn-' + this.userColor ]" @click="this.clearBasket()">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-basket3" viewBox="0 0 16 16">
            <path d="M5.757 1.071a.5.5 0 0 1 .172.686L3.383 6h9.234L10.07 1.757a.5.5 0 1 1 .858-.514L13.783 6H15.5a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5H.5a.5.5 0 0 1-.5-.5v-1A.5.5 0 0 1 .5 6h1.717L5.07 1.243a.5.5 0 0 1 .686-.172zM3.394 15l-1.48-6h-.97l1.525 6.426a.75.75 0 0 0 .729.574h9.606a.75.75 0 0 0 .73-.574L15.056 9h-.972l-1.479 6h-9.21z"/>
            <path d="M 6.854 9.646 a 0.5 0.5 0 1 0 -0.708 0.708 L 7.293 11.5 L 6.146 12.646 a 0.5 0.5 0 1 0 0.708 0.708 L 8 12.207 l 1.146 1.147 a 0.5 0.5 0 0 0 0.708 -0.708 L 8.707 11.5 l 1.147 -1.146 a 0.5 0.5 0 0 0 -0.708 -0.708 L 8 10.793 L 6.854 9.646 z"/>
          </svg>
        </button>
      </div>
    </div>
    <div class="row">
      <div class="list-group pe-0">
        <div v-for="(item, itemSizeKey) in localBasket" :key="itemSizeKey" class="list-group-item d-flex justify-content-between">
          <div class="col-2">
            <span class="badge rounded-pill border" :class="['bg-' + this.matchUiColorWithBuiltIn + '-subtle', 'border-' + this.matchUiColorWithBuiltIn + '-subtle','text-' + this.matchUiColorWithBuiltIn + '-emphasis']">{{  item.quantity }} x</span>
          </div>
          <div class="col-8">
            <span>{{ item.name }} ({{item.size}}) - {{item.price}}</span>
          </div>
          <div class="col-2 text-end">
            <button @click="this.deleteFromBasket(itemSizeKey, item)" type="button" title="Törlés" class="btn btn-close"></button>
          </div>
        </div>
        <div v-if="isBasketEmpty" class="list-group-item d-flex justify-content-center">
          <div class="d-inline">
            <span>
              Üres a kosarad
            </span>
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-basket3 mb-1" viewBox="0 0 16 16">
              <path d="M5.757 1.071a.5.5 0 0 1 .172.686L3.383 6h9.234L10.07 1.757a.5.5 0 1 1 .858-.514L13.783 6H15.5a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5H.5a.5.5 0 0 1-.5-.5v-1A.5.5 0 0 1 .5 6h1.717L5.07 1.243a.5.5 0 0 1 .686-.172zM3.394 15l-1.48-6h-.97l1.525 6.426a.75.75 0 0 0 .729.574h9.606a.75.75 0 0 0 .73-.574L15.056 9h-.972l-1.479 6h-9.21z"/>
            </svg>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { socket, state } from "@/socket";
import { watch } from "vue";

export default {
  name: 'LocalBasket',
  data() {
    return {
      basket: {}
    };
  },
  setup() {
    watch(() => state.user.username, () => {
      fetch(`http://${window.location.host}/api/order/get-user-basket`,{
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          'user': state.user.username,
          'date': new Date().toISOString().split('T')[0]
        })
      })
        .then(response => response.json())
          .then(data => {
            state.localBasket = data;
          })
        .catch(error => console.error(error));
    })
  },
  mounted() {
    this.updateLocalBasket();
  },
  methods: {
    deleteFromBasket: function(itemSizeKey, basketItem) {
      if ( state.orderState === 'order') {
        alert("Figyelem! A rendelő elkezdte áthelyezni a falusiba a kosarat és lehet, hogy nem veszi észre, hogy te változtattál a kosaradon. Jelezd neki mielött nem késő!")
      }
      if ( state.orderState === 'closed') {
        alert("A rendelés már el lett küldve. Már nem módosíthatod a kosaradat.")
        return;
      }
      if (basketItem.quantity == 1) {
        // Otherwise, remove the entry from the basket
        delete state.localBasket[itemSizeKey];
      } else {
        // If the item exists in the basket, decrement the quantity
        basketItem.quantity -= 1;
      }
      socket.emit("Server Basket Update", { "userid": state.user.id, "basket": state.localBasket });

    },
    updateLocalBasket: function() {
      if (state.user.username === undefined) {
        return;
      }
      fetch(`http://${window.location.host}/api/order/get-user-basket`,{
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({"user": state.user.username,'date': new Date().toISOString().split('T')[0]})
      })
        .then(response => response.json())
          .then(data => {
            state.localBasket = data;
          })
        .catch(error => console.error(error));
    },
    clearBasket: function() {
      if ( state.orderState === 'order') {
        alert("Figyelem! A rendelő elkezdte áthelyezni a falusiba a kosarat és lehet, hogy nem veszi észre, hogy te változtattál a kosaradon. Jelezd neki mielött nem késő!")
      }
      if ( state.orderState === 'closed') {
        alert("A rendelés már el lett küldve. Már nem módosíthatod a kosaradat.")
        return;
      }
      socket.emit("Server Basket Update", { "userid": state.user.id, "basket": {} });
    }
  },
  computed: {
    localBasket() {
      return state.localBasket;
    },
    isBasketEmpty() {
      return Object.keys(state.localBasket).length == 0;
    },
    sumBasket() {
      let sum = 0;
      Object.values(state.localBasket).forEach(item => {
        sum+= Number(item.quantity) * Number((item.price).split(' ')[0]);
      });
      return sum;
    },
    matchUiColorWithBuiltIn() {
      switch (this.userColor) {
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
    },
    userColor() {
      return state.user.ui_color ? state.user.ui_color : "falusi";
    }
  }
}
</script>

<style>
</style>
