<template>
  <div class="card">
    <div class="align-items-center card-header row d-flex p-1">
      <div class="col-2 col-lg-1 my-auto">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="28"
          height="28"
          fill="currentColor"
          class="bi bi-cart4 mb-1"
          viewBox="0 0 16 16"
        >
          <path d="M0 2.5A.5.5 0 0 1 .5 2H2a.5.5 0 0 1 .485.379L2.89 4H14.5a.5.5 0 0 1 .485.621l-1.5 6A.5.5 0 0 1 13 11H4a.5.5 0 0 1-.485-.379L1.61 3H.5a.5.5 0 0 1-.5-.5zM3.14 5l.5 2H5V5H3.14zM6 5v2h2V5H6zm3 0v2h2V5H9zm3 0v2h1.36l.5-2H12zm1.11 3H12v2h.61l.5-2zM11 8H9v2h2V8zM8 8H6v2h2V8zM5 8H3.89l.5 2H5V8zm0 5a1 1 0 1 0 0 2 1 1 0 0 0 0-2zm-2 1a2 2 0 1 1 4 0 2 2 0 0 1-4 0zm9-1a1 1 0 1 0 0 2 1 1 0 0 0 0-2zm-2 1a2 2 0 1 1 4 0 2 2 0 0 1-4 0z" />
        </svg>
      </div>
      <div class="col-5 text-start my-auto d-none d-sm-inline d-md-none d-lg-inline">
        <span class="fs-2 text-nowrap">Közös kosár</span>
      </div>
      <div class="col-3 align-items-center p-0 text-center ms-auto">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          fill="currentColor"
          class="bi bi-cash-stack mb-1 me-1"
          viewBox="0 0 16 16"
        >
          <path d="M1 3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1H1zm7 8a2 2 0 1 0 0-4 2 2 0 0 0 0 4z" />
          <path d="M0 5a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H1a1 1 0 0 1-1-1V5zm3 0a2 2 0 0 1-2 2v4a2 2 0 0 1 2 2h10a2 2 0 0 1 2-2V7a2 2 0 0 1-2-2H3z" />
        </svg>
        <span>{{ basketSum }} Ft</span>
      </div>
      <div class="col-3 align-items-center p-0 text-center">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          fill="currentColor"
          class="bi bi-people mb-1 me-1"
          viewBox="0 0 16 16"
        >
          <path d="M15 14s1 0 1-1-1-4-5-4-5 3-5 4 1 1 1 1h8Zm-7.978-1A.261.261 0 0 1 7 12.996c.001-.264.167-1.03.76-1.72C8.312 10.629 9.282 10 11 10c1.717 0 2.687.63 3.24 1.276.593.69.758 1.457.76 1.72l-.008.002a.274.274 0 0 1-.014.002H7.022ZM11 7a2 2 0 1 0 0-4 2 2 0 0 0 0 4Zm3-2a3 3 0 1 1-6 0 3 3 0 0 1 6 0ZM6.936 9.28a5.88 5.88 0 0 0-1.23-.247A7.35 7.35 0 0 0 5 9c-4 0-5 3-5 4 0 .667.333 1 1 1h4.216A2.238 2.238 0 0 1 5 13c0-1.01.377-2.042 1.09-2.904.243-.294.526-.569.846-.816ZM4.92 10A5.493 5.493 0 0 0 4 13H1c0-.26.164-1.03.76-1.724.545-.636 1.492-1.256 3.16-1.275ZM1.5 5.5a3 3 0 1 1 6 0 3 3 0 0 1-6 0Zm3-2a2 2 0 1 0 0 4 2 2 0 0 0 0-4Z" />
        </svg>
        <span>{{ personCount }} fő</span>
      </div>
    </div>
    <div
      v-for="(value, key) in waitingFor"
      :key="key"
      class="row mt-1 mb-1"
    >
      <div class="card">
        <div
          v-if="value == 'sub'"
          class="card-header row d-flex bg-danger-subtle rounded"
        >
          <div class="col-6">
            <span>{{ key }}</span>
          </div>
          <div class="col-6 text-end">
            <span class="me-2">Még nem választott</span>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="18"
              height="18"
              fill="currentColor"
              class="bi bi-emoji-frown"
              viewBox="0 0 16 16"
            >
              <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
              <path d="M4.285 12.433a.5.5 0 0 0 .683-.183A3.498 3.498 0 0 1 8 10.5c1.295 0 2.426.703 3.032 1.75a.5.5 0 0 0 .866-.5A4.498 4.498 0 0 0 8 9.5a4.5 4.5 0 0 0-3.898 2.25.5.5 0 0 0 .183.683zM7 6.5C7 7.328 6.552 8 6 8s-1-.672-1-1.5S5.448 5 6 5s1 .672 1 1.5zm4 0c0 .828-.448 1.5-1 1.5s-1-.672-1-1.5S9.448 5 10 5s1 .672 1 1.5z" />
            </svg>
          </div>
        </div>
        <div
          v-if="value == 'video'"
          class="card-header row d-flex bg-warning-subtle"
        >
          <div class="col-6">
            <span>{{ key }}</span>
          </div>
          <div class="col-6 text-end text-nowrap">
            <span class="me-2">Videóra vár</span>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="18"
              height="18"
              fill="currentColor"
              class="bi bi-person-video3"
              viewBox="0 0 16 16"
            >
              <path d="M6.79 5.093A.5.5 0 0 0 6 5.5v5a.5.5 0 0 0 .79.407l3.5-2.5a.5.5 0 0 0 0-.814l-3.5-2.5z" />
              <path d="M0 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V4zm15 0a1 1 0 0 0-1-1H2a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4z" />
            </svg>
          </div>
        </div>
      </div>
    </div>
    <div
      v-for="(user_entry) in globalBasket"
      :key="user_entry.id"
      class="row mt-1 mb-1"
    >
      <GlobalBasketPerson
        :name="user_entry.username"
        :person-basket="user_entry.basket_entry"
        :collapsable="false"
      />
    </div>
  </div>
</template>

<script>
import { state } from "@/socket";
import { basketSum, personCount } from "@/basket";
import GlobalBasketPerson from './GlobalBasketPerson.vue'

export default {
  name: 'GlobalBasket',
  components: {
    GlobalBasketPerson
  },
  setup() {
    return {
      basketSum,
      personCount
    }
  },
  computed: {
    transportFee() {
      return state.selected_vendor.settings.transport_price.value
    },
    globalBasket() {
      return state.basket;
    },
    waitingFor() {
      const userStates = structuredClone(state.userStates);
      let pickedList = Object.keys(state.basket)

      for (const [key, value] of Object.entries(state.userStates)) {
        if (value === 'none' || value === 'skip') {
          delete userStates[key];
        }
        if (pickedList.includes(key)) {
          delete userStates[key];
        }
      }
      return userStates;
    }
  }
}
</script>

<style>
</style>
