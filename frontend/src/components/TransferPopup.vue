<template>
  <button class="btn btn-warning" id="transferBasketButton" @click="this.openPopup()">Áthelyezés falusiba</button>

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
    <p>Okézd le , ha kifizetted a rendelést</p>
  </Popup>
</template>

<script>
import Popup from './Popup.vue';
import { state, socket } from "@/socket";

export default {
  name: 'TransferPopup',
  components: {
    Popup
  },
  data() {
    return {
      showInitial: false,
      showSpinner: false,
      showFinish: true,
      psid: ""
    }
  },
  methods: {
    transferBasketToFalusi: function() {
      console.log("PSID:"+this.psid);
      if (this.psid !== "") {
        this.showInitial = false;
        this.showSpinner = true;
        fetch(`http://${window.location.hostname}/api/transferBasket`,{
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

              alert("Valami hiba történt.");
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
