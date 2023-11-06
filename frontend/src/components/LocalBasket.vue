<template>
  <div class="card">
    <div class="card-header row d-flex justify-content-between p-1">
      <div class="col-2 col-lg-1 my-auto">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="28"
          height="28"
          fill="currentColor"
          class="bi bi-basket2 mb-1"
          viewBox="0 0 16 16"
        >
          <path d="M4 10a1 1 0 0 1 2 0v2a1 1 0 0 1-2 0v-2zm3 0a1 1 0 0 1 2 0v2a1 1 0 0 1-2 0v-2zm3 0a1 1 0 1 1 2 0v2a1 1 0 0 1-2 0v-2z" />
          <path d="M5.757 1.071a.5.5 0 0 1 .172.686L3.383 6h9.234L10.07 1.757a.5.5 0 1 1 .858-.514L13.783 6H15.5a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-.623l-1.844 6.456a.75.75 0 0 1-.722.544H3.69a.75.75 0 0 1-.722-.544L1.123 8H.5a.5.5 0 0 1-.5-.5v-1A.5.5 0 0 1 .5 6h1.717L5.07 1.243a.5.5 0 0 1 .686-.172zM2.163 8l1.714 6h8.246l1.714-6H2.163z" />
        </svg>
      </div>
      <div class="col-3 col-lg-4 d-none d-sm-inline d-md-none d-lg-inline text-start my-auto">
        <h2 class="text-nowrap">
          Kosarad
        </h2>
      </div>
      <div class="col-7 col-sm-3 col-md-7 col-lg-5 text-center m-auto">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          fill="currentColor"
          class="bi bi-cash me-1 mb-1"
          viewBox="0 0 16 16"
        >
          <path d="M8 10a2 2 0 1 0 0-4 2 2 0 0 0 0 4z" />
          <path d="M0 4a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H1a1 1 0 0 1-1-1V4zm3 0a2 2 0 0 1-2 2v4a2 2 0 0 1 2 2h10a2 2 0 0 1 2-2V6a2 2 0 0 1-2-2H3z" />
        </svg>
        <span title="A fizetendő összeg még változhat, a rendelést leadó személyek számától.(Szállítási díjat több fele osztjuk)">{{ sumBasket }} Ft</span>
      </div>
    </div>
    <div class="row">
      <div class="list-group pe-0">
        <div
          v-if="auth.isLoggedIn"
          class="row px-0 d-flex card-header m-1 mt-0 border border-2 border-top-0 rounded-bottom rounded-top-0"
        >
          <div class="col-12 d-flex justify-content-evenly">
            <div
              v-if="auth.isLoggedIn"
              data-bs-toggle="tooltip"
              data-bs-placement="bottom"
              data-bs-trigger="hover"
              title="Ha az étel címe nem győzött meg és szeretnéd megvárni a mai videót akkor ezzel jelezheted. Ekkor bekerül a neved a közös kosárba és biztos, hogy nem maradsz le a rendelésről. "
            >
              <button
                type="button"
                class="btn me-2 text-nowrap"
                :class="['btn-outline-' + auth.userColor.value, currentUserState === 'video' ? 'active' : '']"
                @click="waitForMe(currentUserState == 'video' ? 'none' : 'video')"
              >
                <div>
                  <span class="d-none d-sm-inline d-md-none d-xl-inline me-2">Videóra várok</span>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    fill="currentColor"
                    class="bi bi-person-video3"
                    viewBox="0 0 16 16"
                  >
                    <path d="M6.79 5.093A.5.5 0 0 0 6 5.5v5a.5.5 0 0 0 .79.407l3.5-2.5a.5.5 0 0 0 0-.814l-3.5-2.5z" />
                    <path d="M0 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V4zm15 0a1 1 0 0 0-1-1H2a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4z" />
                  </svg>
                </div>
              </button>
            </div>
            <div
              v-if="auth.isLoggedIn && subscriptionState == 'full'"
              data-bs-toggle="tooltip"
              data-bs-placement="bottom"
              data-bs-trigger="hover"
              title="Ha feliratkoztál viszont ma hoztál magadnak ebédet vagy máshol eszel akkor ezzel tudod jelezni, hogy ne várjanak rád. Így kikerül a neved a közös kosárból egy nap erejéig de másnap ugyan úgy megjelensz amíg újra nem jelzed ezt."
            >
              <button
                type="button"
                class="btn me-2 text-nowrap"
                :class="['btn-outline-' + auth.userColor.value, currentUserState === 'skip' ? 'active' : '']"
                @click="waitForMe(currentUserState == 'skip' ? 'none' : 'skip')"
              >
                <div>
                  <span class="d-none d-sm-inline d-md-none d-xl-inline me-1">Nem kérek</span>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    fill="currentColor"
                    class="bi bi-cart-dash"
                    viewBox="0 0 16 16"
                  >
                    <path d="M6.5 7a.5.5 0 0 0 0 1h4a.5.5 0 0 0 0-1h-4z" />
                    <path d="M.5 1a.5.5 0 0 0 0 1h1.11l.401 1.607 1.498 7.985A.5.5 0 0 0 4 12h1a2 2 0 1 0 0 4 2 2 0 0 0 0-4h7a2 2 0 1 0 0 4 2 2 0 0 0 0-4h1a.5.5 0 0 0 .491-.408l1.5-8A.5.5 0 0 0 14.5 3H2.89l-.405-1.621A.5.5 0 0 0 2 1H.5zm3.915 10L3.102 4h10.796l-1.313 7h-8.17zM6 14a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm7 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0z" />
                  </svg>
                </div>
              </button>
            </div>
            <div
              data-bs-toggle="tooltip"
              data-bs-placement="bottom"
              data-bs-trigger="hover"
              title="Töröl mindent a kosaradból"
            >
              <button
                class="btn text-nowrap"
                :class="['btn-outline-' + auth.userColor.value ]"
                @click="clearBasket()"
              >
                <span class="d-none d-sm-inline d-md-none d-xl-inline me-1">Törlés</span>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="20"
                  height="20"
                  fill="currentColor"
                  class="bi bi-trash text-bold"
                  viewBox="0 0 16 16"
                >
                  <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5Zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5Zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6Z" />
                  <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1ZM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118ZM2.5 3h11V2h-11v1Z" />
                </svg>
              </button>
            </div>
          </div>
        </div>
        <div
          v-for="(item, itemSizeKey) in localBasket"
          :key="itemSizeKey"
          class="list-group-item d-flex justify-content-between"
        >
          <div class="col-2">
            <span
              class="badge rounded-pill border"
              :class="['bg-' + auth.matchUiColorWithBuiltIn.value + '-subtle', 'border-' + auth.matchUiColorWithBuiltIn.value + '-subtle','text-' + auth.matchUiColorWithBuiltIn.value + '-emphasis']"
            >{{ item.quantity }} x</span>
          </div>
          <div class="col-8">
            <span>{{ item.name }} ({{ item.size }}) - {{ item.price }}</span>
          </div>
          <div class="col-2 text-end">
            <button
              type="button"
              title="Törlés"
              class="btn btn-close"
              @click="deleteFromBasket(itemSizeKey, item)"
            />
          </div>
        </div>
        <div
          v-if="isBasketEmpty"
          class="list-group-item d-flex justify-content-center"
        >
          <div class="d-inline">
            <div v-if="!isBasketEmpty">
              <span class="me-1">Sikerült választanod</span>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                fill="currentColor"
                class="bi bi-basket3 mb-1"
                viewBox="0 0 16 16"
              >
                <path d="M5.757 1.071a.5.5 0 0 1 .172.686L3.383 6h9.234L10.07 1.757a.5.5 0 1 1 .858-.514L13.783 6H15.5a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5H.5a.5.5 0 0 1-.5-.5v-1A.5.5 0 0 1 .5 6h1.717L5.07 1.243a.5.5 0 0 1 .686-.172zM3.394 15l-1.48-6h-.97l1.525 6.426a.75.75 0 0 0 .729.574h9.606a.75.75 0 0 0 .73-.574L15.056 9h-.972l-1.479 6h-9.21z" />
              </svg>
            </div>
            <div v-else-if="auth.isLoggedIn && currentUserState == 'skip'">
              <span class="me-1">Ma nem kérsz</span>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                fill="currentColor"
                class="bi bi-basket3 mb-1"
                viewBox="0 0 16 16"
              >
                <path d="M6.5 7a.5.5 0 0 0 0 1h4a.5.5 0 0 0 0-1h-4z" />
                <path d="M.5 1a.5.5 0 0 0 0 1h1.11l.401 1.607 1.498 7.985A.5.5 0 0 0 4 12h1a2 2 0 1 0 0 4 2 2 0 0 0 0-4h7a2 2 0 1 0 0 4 2 2 0 0 0 0-4h1a.5.5 0 0 0 .491-.408l1.5-8A.5.5 0 0 0 14.5 3H2.89l-.405-1.621A.5.5 0 0 0 2 1H.5zm3.915 10L3.102 4h10.796l-1.313 7h-8.17zM6 14a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm7 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0z" />
              </svg>
            </div>
            <div v-else-if="auth.isLoggedIn && currentUserState == 'video'">
              <span class="me-1">Videóra vársz</span>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                fill="currentColor"
                class="bi bi-basket3 ms-1"
                viewBox="0 0 16 16"
              >
                <path d="M6.79 5.093A.5.5 0 0 0 6 5.5v5a.5.5 0 0 0 .79.407l3.5-2.5a.5.5 0 0 0 0-.814l-3.5-2.5z" />
                <path d="M0 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V4zm15 0a1 1 0 0 0-1-1H2a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4z" />
              </svg>
            </div>
            <div v-else-if="auth.isLoggedIn && subscriptionState == 'full'">
              <span class="me-1">Még nem választottál</span>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                fill="currentColor"
                class="bi bi-emoji-frown"
                viewBox="0 0 16 16"
              >
                <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
                <path d="M4.285 12.433a.5.5 0 0 0 .683-.183A3.498 3.498 0 0 1 8 10.5c1.295 0 2.426.703 3.032 1.75a.5.5 0 0 0 .866-.5A4.498 4.498 0 0 0 8 9.5a4.5 4.5 0 0 0-3.898 2.25.5.5 0 0 0 .183.683zM7 6.5C7 7.328 6.552 8 6 8s-1-.672-1-1.5S5.448 5 6 5s1 .672 1 1.5zm4 0c0 .828-.448 1.5-1 1.5s-1-.672-1-1.5S9.448 5 10 5s1 .672 1 1.5z" />
              </svg>
            </div>
            <div v-else>
              <span class="me-1">Üres a kosarad</span>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                fill="currentColor"
                class="bi bi-basket3 mb-1"
                viewBox="0 0 16 16"
              >
                <path d="M5.757 1.071a.5.5 0 0 1 .172.686L3.383 6h9.234L10.07 1.757a.5.5 0 1 1 .858-.514L13.783 6H15.5a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5H.5a.5.5 0 0 1-.5-.5v-1A.5.5 0 0 1 .5 6h1.717L5.07 1.243a.5.5 0 0 1 .686-.172zM3.394 15l-1.48-6h-.97l1.525 6.426a.75.75 0 0 0 .729.574h9.606a.75.75 0 0 0 .73-.574L15.056 9h-.972l-1.479 6h-9.21z" />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { socket, state } from "@/socket";
import { useAuth } from "@/auth";
import { transportFeePerPerson } from "@/basket";
import { watch } from "vue";
import { notify } from "@kyvg/vue3-notification";

export default {
  name: 'LocalBasket',
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

    const auth = useAuth();
    return {
      auth,
      transportFeePerPerson
    }

  },
  data() {
    return {
      basket: {}
    };
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
      let pearsonCount = Object.keys(state.globalBasket).length;
      if (pearsonCount != 0) {
        sum += Math.ceil(this.transportFeePerPerson/pearsonCount);
      }
      return sum;
    },
    currentUserState() {
      return state.userStates[state.user.username];
    },
    subscriptionState() {
      return state.user.subscribed;
    }
  },
  mounted() {
    this.updateLocalBasket();
    },
  methods: {
    waitForMe: function(waitType) {
      if (waitType === 'skip') {
        if ( state.orderState === 'closed') {
          notify({
            type: "warn",
            text: "A rendelés már el lett küldve.",
          });
          return;
        }
        socket.emit("Server Basket Update", { "userid": state.user.id, "basket": {}, "order_date": state.selectedDate.toISOString().split('T')[0] });
      }
      socket.emit("User Daily State Change",{ 'id': state.user.id, 'new_state':waitType });
    },
    deleteFromBasket: function(itemSizeKey, basketItem) {
      if ( state.orderState === 'closed') {
        notify({
          type: "warn",
          text: "A rendelés már el lett küldve. Már nem módosíthatod a kosaradat.",
        });
        return;
      }
      if (basketItem.quantity == 1) {
        // Otherwise, remove the entry from the basket
        delete state.localBasket[itemSizeKey];
      } else {
        // If the item exists in the basket, decrement the quantity
        basketItem.quantity -= 1;
      }
      socket.emit("Server Basket Update", { "userid": state.user.id, "basket": state.localBasket, "order_date": state.selectedDate.toISOString().split('T')[0] });

    },
    updateLocalBasket: function() {
      if (!this.auth.isLoggedIn.value) {
        return;
      }
      fetch(`http://${window.location.host}/api/order/get-user-basket`,{
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({"user": state.user.username,'date': state.selectedDate.toISOString().split('T')[0]})
      })
        .then(response => response.json())
          .then(data => {
            state.localBasket = data;
          })
        .catch(error => console.error(error));
    },
    clearBasket: function() {
      if ( state.orderState === 'closed') {
        notify({
          type: "warn",
          text: "A rendelés már el lett küldve. Már nem módosíthatod a kosaradat.",
        });
        return;
      }
      socket.emit("Server Basket Update", { "userid": state.user.id, "basket": {}, "order_date": state.selectedDate.toISOString().split('T')[0] });
    }
  }
}
</script>

<style>
</style>
