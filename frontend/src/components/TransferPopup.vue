<template>
  <button class="btn" :class="['btn-' + this.usercolor ]" id="transferBasketButton" @click="this.openPopup()">Áthelyezés falusiba</button>

  <Popup
    :showModal="showInitial"
    title="Ez a Rendelő ember feladata"
    @cancel="showInitial = false"
    @confirm="this.transferBasketToFalusi()"
  >
    <p>Írd be a falusi oldalon lévő PHPSESSIONID-det:</p>
    <p>Falusi oldalán a cookie-k között kell keresned ezt a változót.
      Legyél bejelentkezve a falusiba! Az értékét másold ide:</p>
    PHPSESSIONID: <input type="text" v-model.trim="psid">
  </Popup>
  <teleport to="body">
    <div v-if="showSpinner" class="overlay d-flex justify-content-center">
      <div class="spinner-border text-center text-dark" style="width: 4rem; height: 4rem; z-index: 20;" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
  </teleport>
  <Popup
    :showModal="showFinish"
    title="Rendelés befejezése"
    @cancel="showFinish = false"
    @confirm="this.orderPayed()"
  >
    <p>Kosár sikeresen átmásolva a falusira. Frissítsd a falusi oldalát.</p>
    <p>
    Rendelés megjegyzés példa:
    </p>
    <div class="d-flex">
      <div class="border bg-light-subtle rounded ps-2">
        <code class="user-select-all">{{ this.orderDesc }}</code>
      </div>
      <button type="button" name="button" title="Copy to clipboard" class="btn " @click="this.doCopy()">
        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="currentColor" class="bi bi-clipboard2" viewBox="0 0 16 16">
          <path d="M3.5 2a.5.5 0 0 0-.5.5v12a.5.5 0 0 0 .5.5h9a.5.5 0 0 0 .5-.5v-12a.5.5 0 0 0-.5-.5H12a.5.5 0 0 1 0-1h.5A1.5 1.5 0 0 1 14 2.5v12a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 2 14.5v-12A1.5 1.5 0 0 1 3.5 1H4a.5.5 0 0 1 0 1h-.5Z"/>
          <path d="M10 .5a.5.5 0 0 0-.5-.5h-3a.5.5 0 0 0-.5.5.5.5 0 0 1-.5.5.5.5 0 0 0-.5.5V2a.5.5 0 0 0 .5.5h5A.5.5 0 0 0 11 2v-.5a.5.5 0 0 0-.5-.5.5.5 0 0 1-.5-.5Z"/>
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
import { copyText } from 'vue3-clipboard';

export default {
  name: 'TransferPopup',
  components: {
    Popup
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
          body: JSON.stringify({ psid: this.psid })
        })
          .then(response => {
            this.showSpinner = false;
            if (response.statusText == "OK") {
              this.showFinish = true;
            } else {
              this.showSpinner = false;
              alert("Valami hiba történt. Hiba: " + response);
            }
          })
            .catch(error => console.error(error))
      }
    },
    openPopup: function() {
      if (state.orderState === 'closed') {
        alert("Ma már rendeltek!")
        return
      } else {
        this.showInitial = true;
      }
    },
    orderPayed: function() {
      socket.emit("Ordered and Payed");
      this.showFinish = false;
    },
    doCopy: function() {
      copyText(this.orderDesc, undefined, (error, event) =>{
        if (error) {
           alert('Can not copy')
           console.log(error)
         } else {
           alert('Copied')
           console.log(event)
         }
      });
    }
  },
  computed: {
    usercolor(){
      return state.user.ui_color ? state.user.ui_color : "falusi";
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
