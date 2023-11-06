<template>
    <div class="card" :class="this.name === this.loggedInUser ? 'border border-2 border-'+ auth.matchUiColorWithBuiltIn.value + (this.usertheme === 'dark' ? '-subtle' : '') : ''">
      <div class="card-header row d-flex pe-0">
        <div class="col-6">
          <span>{{ name }}</span>
          <a v-if="copyable && name !== loggedInUser" class="ms-2 p-1 btn btn-sm" :class="['btn-' + auth.userColor.value ]" @click="copy">
            Másol
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-clipboard2" viewBox="0 0 16 16">
              <path d="M3.5 2a.5.5 0 0 0-.5.5v12a.5.5 0 0 0 .5.5h9a.5.5 0 0 0 .5-.5v-12a.5.5 0 0 0-.5-.5H12a.5.5 0 0 1 0-1h.5A1.5 1.5 0 0 1 14 2.5v12a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 2 14.5v-12A1.5 1.5 0 0 1 3.5 1H4a.5.5 0 0 1 0 1h-.5Z"/>
              <path d="M10 .5a.5.5 0 0 0-.5-.5h-3a.5.5 0 0 0-.5.5.5.5 0 0 1-.5.5.5.5 0 0 0-.5.5V2a.5.5 0 0 0 .5.5h5A.5.5 0 0 0 11 2v-.5a.5.5 0 0 0-.5-.5.5.5 0 0 1-.5-.5Z"/>
            </svg>
          </a>
        </div>
        <div class="col-6 d-flex justify-content-end">
          <span class="me-2" :title="this.basketTotalTitle">{{ this.basketTotal }} Ft</span>
          <a
            v-if="collapsable"
            class="link-underline link-underline-opacity-0"
            data-bs-toggle="collapse"
            :data-bs-target="'#' + (name.replace(/[^a-z0-9]/ig, ''))"
            role="button" :aria-expanded="!collapsable || !startCollapsed"
            :aria-controls="name">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-caret-down" viewBox="0 0 16 16">
              <path d="M3.204 5h9.592L8 10.481 3.204 5zm-.753.659 4.796 5.48a1 1 0 0 0 1.506 0l4.796-5.48c.566-.647.106-1.659-.753-1.659H3.204a1 1 0 0 0-.753 1.659z"/>
            </svg>
          </a>
        </div>
      </div>
      <div
        class="row list-group"
        :class="{ show: !collapsable || !startCollapsed, collapse: startCollapsed}"
        :id="collapsable ? (name.replace(/[^a-z0-9]/ig, '')) : false">
        <div v-for="item in personBasket" :key="item.id" class="list-group-item  d-flex justify-content-between align-items-center"  >
          <span
            class="badge rounded-pill border me-2 col-1"
            :class="[
              'bg-' + auth.matchUiColorWithBuiltIn.value + '-subtle',
              'border-' + auth.matchUiColorWithBuiltIn.value + '-subtle',
              'text-' + auth.matchUiColorWithBuiltIn.value + '-emphasis']">
            {{ item.quantity }} x
          </span>
          <span class="col-7">{{ item.name }}</span>
          <div class="col-3 row mx-0">
            <span class="col-12 col-lg-6 d-flex justify-content-center justify-content-lg-start text-nowrap px-0">{{ item.size.split(' ')[0] }}</span>
            <span class="col-12 col-lg-6 d-flex justify-content-center justify-content-lg-end text-nowrap pe-0">{{ item.price }}</span>
          </div>
        </div>
      </div>
    </div>
</template>

<script>
import { state, socket } from "@/socket";
import { useAuth } from "@/auth";
import { transportFeePerPerson } from "@/basket";
import { notify } from "@kyvg/vue3-notification";

export default {
  name: 'PersonComponent',
  props: {
    'name':{
      type: String
    },
    'personBasket':{
      type: Object
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
  data() {
    return {
      sum: 0
    };
  },
  setup() {
    const auth = useAuth();
    return {
      auth,
      transportFeePerPerson
    };
  },
  methods: {
    copy: function() {
      if (!this.auth.isLoggedIn.value) {
        notify({
          type: "warn",
          text: "Jelentkezz be a rendeléshez!",
        });
        return;
      }
      socket.emit("Server Basket Update", { "userid": state.user.id, "basket": this.personBasket, "order_date": state.selectedDate.toISOString().split('T')[0] });
      notify({
        type: "info",
        text: "Másolva",
      });
    }
  },
  computed: {
    basketTotal() {
      let sum=0;
      Object.values(this.personBasket).forEach((item) => {
        sum+= Number(item.quantity) * Number((item.price).split(' ')[0]);
      })
      sum += Number(this.transportFeePerPerson);
      return sum;
    },
    basketTotalTitle() {
      let sumTitle = ""
      Object.values(this.personBasket).forEach((item) => {
        sumTitle+= item.quantity + '*' + item.price + ' + ';
      })
      sumTitle+= this.transportFeePerPerson + ' Ft(Szállítási díj) = ' + this.sum + ' Ft';
      return sumTitle;
    },
    loggedInUser() {
      return state.user.username
    },
    usertheme() {
      return state.user.ui_theme ? state.user.ui_theme : "light";
    }
  }
}
</script>

<style>
</style>
