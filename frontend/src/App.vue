<template>
  <div class="popup" id="popup">
    <div class="popup-inner">
      <h2>Kélek írd be hogyan hívnak:</h2>
      <input type="text" id="username-input">
      <br><br>
      <button class="btn btn-secondary" onclick="saveUsername()">Mentés</button>
      <button class="btn btn-secondary" onclick="closePopup()">Mégse</button>
    </div>
  </div>
  <div class="popup" id="orderend-popup">
    <div class="popup-inner">
      <h2>Kosár sikeresen átmásolva a falusira. Frissítsd a falusi oldalát.</h2>
      <p>Okézd le , ha kifizetted a rendelést</p>
      <br><br>
      <button class="btn btn-secondary" onclick="orderPayed()">Fizetve</button>
      <button class="btn btn-secondary" onclick="closeOrderEndPopup()">Mégse</button>
    </div>
  </div>
  <div class="popup" id="psid-popup">
    <div class="popup-inner">
      <h2>Ez a Rendelő ember feladata</h2>
      <h2>Írd be a falusi oldalon lévő PHPSESSIONID-det:</h2>
      <p>Falusi oldalán a cookie-k között kell keresned ezt a változót. Legyél bejelentkezve a falusiba! Az értékét másold ide:</p>
      <input type="text" id="psid-input">
      <br><br>
      <p>Az áthelyezés eltarthat pár másodpercig, várj a visszajelzésig.</p>
      <button class="btn btn-secondary" onclick="transferBasketToFalusi()">Áthelyezés</button>
      <button class="btn btn-secondary" onclick="closePSIDPopup()">Mégse</button>
    </div>
  </div>
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
      <div class="col-6 text-end d-flex justify-content-end align-items-center user-info">
        <span id="username-display"></span>
        <svg onclick="openPopup()" xmlns="http://www.w3.org/2000/svg" width="15" height="15" fill="currentColor" class="bi bi-pen mt-1" viewBox="0 0 16 16" data-darkreader-inline-fill="" style="--darkreader-inline-fill:currentColor;">
          <path d="m13.498.795.149-.149a1.207 1.207 0 1 1 1.707 1.708l-.149.148a1.5 1.5 0 0 1-.059 2.059L4.854 14.854a.5.5 0 0 1-.233.131l-4 1a.5.5 0 0 1-.606-.606l1-4a.5.5 0 0 1 .131-.232l9.642-9.642a.5.5 0 0 0-.642.056L6.854 4.854a.5.5 0 1 1-.708-.708L9.44.854A1.5 1.5 0 0 1 11.5.796a1.5 1.5 0 0 1 1.998-.001zm-.644.766a.5.5 0 0 0-.707 0L1.95 11.756l-.764 3.057 3.057-.764L14.44 3.854a.5.5 0 0 0 0-.708l-1.585-1.585z"></path>
        </svg>
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
      <div class="col-5">
        <div class="list-container localbasket row">
          <div class="container">
            <div class="row align-items-center">
              <div class="col-4">
                <h2>Kosarad</h2>
              </div>
              <div class="col-4 align-items-center">
                <span id="localbasket-value"></span>
              </div>
              <div class="col-4 text-end">
                <button class="btn btn-secondary" id="clearBasketButton" onclick="clearBasket()">Kosarad ürítése</button>
              </div>
            </div>
            <div class="row">
              <ul class="list" id="basketList"></ul>
            </div>
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
                <button class="btn btn-secondary" id="transferBasketButton" onclick="openPSIDPopup()">Áthelyezés falusiba</button>
              </div>
            </div>
            <div class="row">
              <ul class="list" id="globalbasketList"></ul>
            </div>
          </div>
        </div>
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
    Datestamp
  },
  mounted() {
    orginalScript.main();
  }
}
</script>

<style>
</style>
