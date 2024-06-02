<template>
  <div
    class="card"
    :class="auth.isLoggedIn && name === auth.user.username ? 'border border-2 border-'+ auth.getUserColor + (usertheme === 'dark' ? '-subtle' : '') : ''"
  >
    <div class="card-header row d-flex pe-0">
      <div class="col-6">
        <span>{{ name }}</span>
        <a
          v-if="copyable && name !== auth.user.username"
          class="ms-2 p-1 btn btn-sm"
          :class="['btn-' + auth.getUserColor ]"
          @click="basket.copy()"
        >
          Másol
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            fill="currentColor"
            class="bi bi-clipboard2"
            viewBox="0 0 16 16"
          >
            <path d="M3.5 2a.5.5 0 0 0-.5.5v12a.5.5 0 0 0 .5.5h9a.5.5 0 0 0 .5-.5v-12a.5.5 0 0 0-.5-.5H12a.5.5 0 0 1 0-1h.5A1.5 1.5 0 0 1 14 2.5v12a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 2 14.5v-12A1.5 1.5 0 0 1 3.5 1H4a.5.5 0 0 1 0 1h-.5Z" />
            <path d="M10 .5a.5.5 0 0 0-.5-.5h-3a.5.5 0 0 0-.5.5.5.5 0 0 1-.5.5.5.5 0 0 0-.5.5V2a.5.5 0 0 0 .5.5h5A.5.5 0 0 0 11 2v-.5a.5.5 0 0 0-.5-.5.5.5 0 0 1-.5-.5Z" />
          </svg>
        </a>
      </div>
      <div class="col-6 d-flex justify-content-end">
        <span
          class="me-2"
          :title="basketTotalTitle"
        >{{ basketTotal }} Ft</span>
        <a
          v-if="collapsable"
          class="link-underline link-underline-opacity-0"
          :class="['text-' + auth.getUserColor ]"
          data-bs-toggle="collapse"
          :data-bs-target="'#' + (name.replace(/[^a-z0-9]/ig, ''))"
          role="button"
          :aria-expanded="!collapsable || !startCollapsed"
          :aria-controls="name"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            fill="currentColor"
            class="bi bi-caret-down"
            viewBox="0 0 16 16"
          >
            <path d="M3.204 5h9.592L8 10.481 3.204 5zm-.753.659 4.796 5.48a1 1 0 0 0 1.506 0l4.796-5.48c.566-.647.106-1.659-.753-1.659H3.204a1 1 0 0 0-.753 1.659z" />
          </svg>
        </a>
      </div>
    </div>
    <div
      :id="collapsable ? (name.replace(/[^a-z0-9]/ig, '')) : false"
      class="row list-group"
      :class="{ show: !collapsable || !startCollapsed, collapse: startCollapsed}"
    >
      <div
        v-for="item in personBasket"
        :key="item.item.id"
        class="list-group-item  d-flex justify-content-between align-items-center"
      >
        <span
          class="badge rounded-pill border me-2 col-1"
          :class="[
            'bg-' + auth.getUserColor,
            'border-' + auth.getUserColor + '-subtle']"
        >
          {{ item.count }} x
        </span>
        <span class="col-7">{{ item.item.name }}</span>
        <div class="col-3 row mx-0">
          <span class="col-12 col-lg-6 d-flex justify-content-center justify-content-lg-start text-nowrap px-0">{{ item.item.size.split(' ')[0] }}</span>
          <span class="col-12 col-lg-6 d-flex justify-content-center justify-content-lg-end text-nowrap pe-0">{{ item.item.price }} Ft</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuth } from "@/stores/auth";
import { useBasket } from "@/stores/basket";
import { transportFeePerPerson } from "@/stores/basket";

export default {
  name: 'PersonComponent',
  props: {
    'name':{
      type: String,
      default: ""
    },
    'personBasket':{
      type: Object,
      default: new Object()
    },
    'startCollapsed':{
      type: Boolean,
      default: false
    },
    'collapsable':{
      type: Boolean,
      default: true
    },
    'copyable':{
      type: Boolean,
      default: true
    }
  },
  setup() {
    const auth = useAuth();
    const basket = useBasket();
    return {
      auth,
      basket,
      transportFeePerPerson
    };
  },
  data() {
    return {
      sum: 0
    };
  },
  computed: {
    basketTotal() {
      let sum=0;
      Object.values(this.personBasket).forEach((entry) => {
          sum+= Number(entry.count) * Number(entry.item.price);
      });
      sum += Number(this.basket.transportFeePerPerson);
      return sum;
    },
    basketTotalTitle() {
      let sumTitle = ""
      Object.values(this.personBasket).forEach((entry) => {
          sumTitle+= entry.count + '*' + entry.item.price + ' Ft + ';
      });
      sumTitle+= this.basket.transportFeePerPerson + ' Ft(Szállítási díj) = ' + this.sum + ' Ft';
      return sumTitle;
    },
    loggedInUser() {
      return this.auth.user.username
    },
    usertheme() {
      return this.auth.user.ui_theme ? this.auth.user.ui_theme : "light";
    }
  },
}
</script>

<style>
</style>
