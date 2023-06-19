<template>
  <div class="row d-flex align-items-center">
    <div class="col-7 text-start">
      <div class="align-items-center">
        <h1>Falusi rendelő</h1>
      </div>
    </div>
    <div class="col-5 d-flex ps-0">
      <div class="col-6">
        <button class="btn" id="darkModeToggleButton" onclick="darkModeToggle()">Dark Mode</button>
      </div>
      <div class="col-6 text-end d-flex justify-content-end align-items-center">
          <UsernamePopup/>
      </div>
    </div>
  </div>
  <div class="row">
    <div class="d-flex">
      <div class="list-container etlaplist container col-7 pe-4">
        <div class="row d-flex">
          <div class="col">
            <h2 class="ps-0" id="etlapWithDate">Étlap</h2>
          </div>
          <div id="vueDateStamp" class="col">
            <Datestamp />
          </div>
        </div>
        <div class="list row">
          <ul class="" id="foodList">
            <template id="etlapListItemTemplate">
              <li class="row item">
                <span class="name col"></span>
                <div class="button-container col-4 d-flex justify-content-end">
                </div>
              </li>
            </template>
            <template id="etlapListItemButtonTemplate">
                  <button class="btn btn-secondary btn-sm col-sm-6"></button>
            </template>
          </ul>
        </div>
      </div>
        <div class="list-container globalbasket row">
          <div class="container">
            <div class="row align-items-center">
              <div class="col-4">
                <h2>Közös kosár</h2>
              </div>
              <div class="col-2 align-items-center">
                <span id="globalbasket-value"></span>
              </div>
              <div class="col-2 align-items-center">
                <span id="globalbasket-boxcount"></span>
              </div>
              <div class="col-4 text-end">
                <TransferPopup/>
              </div>
            </div>
            <div class="row">
              <ul class="list" id="globalbasketList"></ul>
            </div>
          </div>
        </div>
    </div>
    <div class="col-5">
      <div class="row p-2">
        <LocalBasket ref="localbasket" @basketUpdate="this.onBasketUpdate()"/>
      </div>
      <div class="row p-2">
      </div>
    </div>
  </div>
  <div class="row d-flex justify-content-between" style="background-color: rgba(0, 0, 0, 0.2);">
    <span class="col-6 text-start">Készítette: Tóth Ákos</span>
    <span class="col-6 text-end">Verzió: v0.4.1</span>
  </div>
</template>


<script>
import Datestamp from './components/DateStamp.vue'
import UsernamePopup from './components/UsernamePopup.vue'
import TransferPopup from './components/TransferPopup.vue'
import LocalBasket from './components/LocalBasket.vue'
import * as orginalScript from '../public/scripts.js';

window.openPopup = orginalScript.openPopup;
window.closePopup = orginalScript.closePopup;
window.saveUsername = orginalScript.saveUsername;
window.transferBasketToFalusi = orginalScript.transferBasketToFalusi;
window.closeOrderEndPopup = orginalScript.closeOrderEndPopup;
window.closePSIDPopup = orginalScript.closePSIDPopup;
window.openPSIDPopup = orginalScript.openPSIDPopup;
window.clearBasket = orginalScript.clearBasket;
window.darkModeToggle = orginalScript.darkModeToggle;

export default {
  name: 'App',
  components: {
    Datestamp,
    UsernamePopup,
    TransferPopup
    LocalBasket,
  setup() {
    const { cookies } = useCookies();
    return { cookies };
  },
  methods: {
    onBasketUpdate: function() {
      this.$refs.localbasket.updateBasket();
      socket.emit("Server Basket Update",{ [this.cookies.get('username')]: this.cookies.get('basket') });
    }
  },
  mounted() {
    orginalScript.main();
  }
}
</script>

<style>
</style>
