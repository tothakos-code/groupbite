<template>
  <button
    id="transferBasketButton"
    class="btn"
    :class="['btn-' + auth.userColor.value ]"
    @click="openPopup()"
  >
    Áthelyezés falusiba
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      fill="currentColor"
      class="bi bi-truck"
      viewBox="0 0 16 16"
    >
      <path d="M0 3.5A1.5 1.5 0 0 1 1.5 2h9A1.5 1.5 0 0 1 12 3.5V5h1.02a1.5 1.5 0 0 1 1.17.563l1.481 1.85a1.5 1.5 0 0 1 .329.938V10.5a1.5 1.5 0 0 1-1.5 1.5H14a2 2 0 1 1-4 0H5a2 2 0 1 1-3.998-.085A1.5 1.5 0 0 1 0 10.5v-7zm1.294 7.456A1.999 1.999 0 0 1 4.732 11h5.536a2.01 2.01 0 0 1 .732-.732V3.5a.5.5 0 0 0-.5-.5h-9a.5.5 0 0 0-.5.5v7a.5.5 0 0 0 .294.456zM12 10a2 2 0 0 1 1.732 1h.768a.5.5 0 0 0 .5-.5V8.35a.5.5 0 0 0-.11-.312l-1.48-1.85A.5.5 0 0 0 13.02 6H12v4zm-9 1a1 1 0 1 0 0 2 1 1 0 0 0 0-2zm9 0a1 1 0 1 0 0 2 1 1 0 0 0 0-2z" />
    </svg>
  </button>

  <Popup
    :show-modal="showInitial"
    title="Ez a Rendelő ember feladata"
    @cancel="showInitial = false"
    @confirm="transferBasketToFalusi()"
  >
    <p>Írd be a falusi oldalon lévő PHPSESSIONID-det:</p>
    <p>
      Falusi oldalán a cookie-k között kell keresned ezt a változót.
      Legyél bejelentkezve a falusiba! Az értékét másold ide:
    </p>
    PHPSESSIONID: <input
      v-model.trim="psid"
      type="text"
    >
  </Popup>
  <teleport to="body">
    <div
      v-if="showSpinner"
      class="overlay d-flex justify-content-center"
    >
      <div
        class="spinner-border text-center text-dark"
        style="width: 4rem; height: 4rem; z-index: 20;"
        role="status"
      >
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
  </teleport>
  <Popup
    :show-modal="showFinish"
    title="Rendelés befejezése"
    @cancel="showFinish = false"
    @confirm="orderPayed()"
  >
    <p>Kosár sikeresen átmásolva a falusira. Frissítsd a falusi oldalát.</p>
    <p>
      Rendelés megjegyzés példa:
    </p>
    <div class="d-flex">
      <div class="border bg-light-subtle rounded ps-2">
        <code class="user-select-all">{{ orderDesc }}</code>
      </div>
      <button
        type="button"
        name="button"
        title="Copy to clipboard"
        class="btn "
        @click="doCopy()"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="28"
          height="28"
          fill="currentColor"
          class="bi bi-clipboard2"
          viewBox="0 0 16 16"
        >
          <path d="M3.5 2a.5.5 0 0 0-.5.5v12a.5.5 0 0 0 .5.5h9a.5.5 0 0 0 .5-.5v-12a.5.5 0 0 0-.5-.5H12a.5.5 0 0 1 0-1h.5A1.5 1.5 0 0 1 14 2.5v12a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 2 14.5v-12A1.5 1.5 0 0 1 3.5 1H4a.5.5 0 0 1 0 1h-.5Z" />
          <path d="M10 .5a.5.5 0 0 0-.5-.5h-3a.5.5 0 0 0-.5.5.5.5 0 0 1-.5.5.5.5 0 0 0-.5.5V2a.5.5 0 0 0 .5.5h5A.5.5 0 0 0 11 2v-.5a.5.5 0 0 0-.5-.5.5.5 0 0 1-.5-.5Z" />
        </svg>
      </button>
    </div>
    <br>
    <p>Okézd le , ha kifizetted a rendelést</p>
  </Popup>
</template>

<script>
import Popup from './Popup.vue';
import { state, socket } from "@/socket";
import { useAuth } from "@/auth";
import { copyText } from 'vue3-clipboard';
import { notify } from "@kyvg/vue3-notification";

export default {
  name: 'TransferPopup',
  components: {
    Popup
  },
  setup() {
    const auth = useAuth();
    return {
      auth
    }
  },
  data() {
    return {
      showInitial: false,
      showSpinner: false,
      showFinish: false,
      orderDesc: "Tigra kft. Csere edényeket adunk. Mindent külön edénybe szeretnénk. Nagyon szépen köszönjük.",
      psid: ""
    }
  },
  methods: {
    transferBasketToFalusi: function() {
      console.log("PSID:"+this.psid);
      if (this.psid !== "") {
        this.showInitial = false;
        this.showSpinner = true;
        fetch(`http://${window.location.host}/api/order/transferBasket`,{
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ psid: this.psid, order_date: state.selectedDate })
        })
          .then(response => {
            this.showSpinner = false;
            if (response.statusText == "OK") {
              this.showFinish = true;
            } else {
              this.showSpinner = false;
              notify({
                type: "error",
                text: "Valami hiba történt. Hiba: " + response,
              });
            }
          })
            .catch(error => console.error(error))
      }
    },
    openPopup: function() {
      if (state.order.state_id === 'closed') {
        notify({
          type: "warn",
          text: "A rendelést ma már elküldték",
        });
        return
      } else {
        this.showInitial = true;
      }
    },
    orderPayed: function() {
      socket.emit("Ordered and Payed", { date: state.selecedDate });
      this.showFinish = false;
    },
    doCopy: function() {
      copyText(this.orderDesc, undefined, (error, event) =>{
        if (error) {
           notify({
             type: "warn",
             text: "Nem sikerült a másolás",
           });
           console.log(error)
         } else {
           notify({
             type: "info",
             text: "Másolva",
           });
           console.log(event)
         }
      });
    }
  }
}
</script>

<style>
.overlay {
    position: fixed;
    width: 100%;
    height: 100%;
    z-index: 1000;
    top: 40%;
    left: 0px;
    opacity: 0.5;
    filter: alpha(opacity=50);
 }
</style>
