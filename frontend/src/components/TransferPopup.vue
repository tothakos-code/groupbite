<template>
  <button class="btn btn-secondary" id="transferBasketButton" @click="this.openPopup()">Áthelyezés falusiba</button>
  <Popup  v-if="showInitial" title="Ez a Rendelő ember feladata" @cancel="showInitial = false" @confirm="this.transferBasketToFalusi()">
    <p>Írd be a falusi oldalon lévő PHPSESSIONID-det:</p>
    <p>Falusi oldalán a cookie-k között kell keresned ezt a változót. Legyél bejelentkezve a falusiba! Az értékét másold ide:</p>
    <input type="text" v-model.trim="psid">
    <p>Az áthelyezés eltarthat pár másodpercig, várj a felugró ablakra.</p>
  </Popup>
  <Popup  v-if="showFinish" title="Kosár sikeresen átmásolva a falusira. Frissítsd a falusi oldalát." @cancel="showFinish = false" @confirm="this.orderPayed()">
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
      showFinish: false,
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
</style>
