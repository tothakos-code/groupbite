<template>
  <div class="row d-flex-inline justify-content-start">
    <div class="col my-auto">
      <button class="btn btn-dark" @click="this.toggleDarkMode()">
        <svg v-if="this.theme === 'light'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-moon-fill" viewBox="0 0 16 16">
          <path d="M6 .278a.768.768 0 0 1 .08.858 7.208 7.208 0 0 0-.878 3.46c0 4.021 3.278 7.277 7.318 7.277.527 0 1.04-.055 1.533-.16a.787.787 0 0 1 .81.316.733.733 0 0 1-.031.893A8.349 8.349 0 0 1 8.344 16C3.734 16 0 12.286 0 7.71 0 4.266 2.114 1.312 5.124.06A.752.752 0 0 1 6 .278z"/>
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-brightness-high-fill" viewBox="0 0 16 16">
          <path d="M12 8a4 4 0 1 1-8 0 4 4 0 0 1 8 0zM8 0a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 0zm0 13a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 13zm8-5a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2a.5.5 0 0 1 .5.5zM3 8a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2A.5.5 0 0 1 3 8zm10.657-5.657a.5.5 0 0 1 0 .707l-1.414 1.415a.5.5 0 1 1-.707-.708l1.414-1.414a.5.5 0 0 1 .707 0zm-9.193 9.193a.5.5 0 0 1 0 .707L3.05 13.657a.5.5 0 0 1-.707-.707l1.414-1.414a.5.5 0 0 1 .707 0zm9.193 2.121a.5.5 0 0 1-.707 0l-1.414-1.414a.5.5 0 0 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .707zM4.464 4.465a.5.5 0 0 1-.707 0L2.343 3.05a.5.5 0 1 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .708z"/>
        </svg>
      </button>
    </div>
    <div v-if="isLoggedIn" class="col d-flex justify-content-start">
      <div class="col my-auto" title="Ha feliratkozol megjelenik a neved minden nap a közös kosárban. Így a többiek látják, hogy még nem választottál és biztos nem maradsz le a rendelésről. Akkor érdemes feliratkozni, ha nagyon sokszor rendelsz a falusiból.">
        <button type="button" class="btn me-2 position-relative" :class="['btn-' + this.userColor ]" @click="this.subscribeToggle()">
          <div v-if="this.subscriptionState != 'full'">
            <!-- <span class="d-none d-lg-inline">Feliratkozás</span> -->
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-repeat" viewBox="0 0 16 16">
              <path d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z"/>
              <path fill-rule="evenodd" d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5.002 5.002 0 0 0 8 3zM3.1 9a5.002 5.002 0 0 0 8.757 2.182.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9H3.1z"/>
            </svg>
            <span class="position-absolute top-0 start-50 translate-middle badge rounded-pill bg-danger">
              <span class="d-none d-lg-inline">Leiratkozva</span>
            </span>
          </div>
          <div v-else>
            <!-- <span class="d-none d-lg-inline">Leiratkozás</span> -->
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-repeat" viewBox="0 0 16 16">
              <path d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z"/>
              <path fill-rule="evenodd" d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5.002 5.002 0 0 0 8 3zM3.1 9a5.002 5.002 0 0 0 8.757 2.182.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9H3.1z"/>
              <path fill-rule="evenodd" d="M13.854 2.146a.5.5 0 0 1 0 .708l-11 11a.5.5 0 0 1-.708-.708l11-11a.5.5 0 0 1 .708 0Z"/>
            </svg>
            <span class="position-absolute top-0 start-50 translate-middle badge rounded-pill bg-success">
              <span class="d-none d-lg-inline">Feliratkozva</span>
            </span>
          </div>
        </button>
      </div>
      <div class="col my-auto" v-if="this.subscriptionState == 'full'" title="Ha feliratkoztál viszont ma hoztál magadnak ebédet vagy máshol eszel akkor ezzel tudod jelezni, hogy ne várjanak rád. Így kikerül a neved a közös kosárból egy nap erejéig de másnap ugyan úgy megjelensz amíg újra nem jelzed ezt.">
        <button
          type="button"
          class="btn me-2 text-nowrap"
          :class="['btn-' + this.userColor ]"
          @click="this.waitForMe(this.currentUserState == 'skip' ? 'none' : 'skip')">
            <span class="d-none d-xl-inline me-1">Nem kérek</span>
            <svg v-if="this.currentUserState == 'skip'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-cart-check" viewBox="0 0 16 16">
              <path d="M11.354 6.354a.5.5 0 0 0-.708-.708L8 8.293 6.854 7.146a.5.5 0 1 0-.708.708l1.5 1.5a.5.5 0 0 0 .708 0l3-3z"/>
              <path d="M.5 1a.5.5 0 0 0 0 1h1.11l.401 1.607 1.498 7.985A.5.5 0 0 0 4 12h1a2 2 0 1 0 0 4 2 2 0 0 0 0-4h7a2 2 0 1 0 0 4 2 2 0 0 0 0-4h1a.5.5 0 0 0 .491-.408l1.5-8A.5.5 0 0 0 14.5 3H2.89l-.405-1.621A.5.5 0 0 0 2 1H.5zm3.915 10L3.102 4h10.796l-1.313 7h-8.17zM6 14a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm7 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"/>
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-cart-dash" viewBox="0 0 16 16">
              <path d="M6.5 7a.5.5 0 0 0 0 1h4a.5.5 0 0 0 0-1h-4z"/>
              <path d="M.5 1a.5.5 0 0 0 0 1h1.11l.401 1.607 1.498 7.985A.5.5 0 0 0 4 12h1a2 2 0 1 0 0 4 2 2 0 0 0 0-4h7a2 2 0 1 0 0 4 2 2 0 0 0 0-4h1a.5.5 0 0 0 .491-.408l1.5-8A.5.5 0 0 0 14.5 3H2.89l-.405-1.621A.5.5 0 0 0 2 1H.5zm3.915 10L3.102 4h10.796l-1.313 7h-8.17zM6 14a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm7 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"/>
            </svg>
        </button>
      </div>
      <div class="col my-auto" v-if="this.currentUserState != 'skip'" title="Ha az étel címe nem győzött meg és szeretnéd megvárni a mai videót akkor ezzel jelezheted. Ekkor bekerül a neved a közös kosárba és biztos, hogy nem maradsz le a rendelésről. ">

        <button
          type="button"
          class="btn me-2 text-nowrap"
          :class="['btn-' + this.userColor ]"
          @click="this.waitForMe(this.currentUserState == 'video' ? 'none' : 'video')"
        >
          <span class="d-none d-xl-inline me-1">Videóra várok</span>
          <svg v-if="this.currentUserState == 'video'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-video3" viewBox="0 0 16 16">
            <path d="M14 9.5a2 2 0 1 1-4 0 2 2 0 0 1 4 0Zm-6 5.7c0 .8.8.8.8.8h6.4s.8 0 .8-.8-.8-3.2-4-3.2-4 2.4-4 3.2Z"/>
            <path d="M2 2a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h5.243c.122-.326.295-.668.526-1H2a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v7.81c.353.23.656.496.91.783.059-.187.09-.386.09-.593V4a2 2 0 0 0-2-2H2Z"/>
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-video3" viewBox="0 0 16 16">
            <path d="M14 9.5a2 2 0 1 1-4 0 2 2 0 0 1 4 0Zm-6 5.7c0 .8.8.8.8.8h6.4s.8 0 .8-.8-.8-3.2-4-3.2-4 2.4-4 3.2Z"/>
            <path d="M2 2a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h5.243c.122-.326.295-.668.526-1H2a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v7.81c.353.23.656.496.91.783.059-.187.09-.386.09-.593V4a2 2 0 0 0-2-2H2Z"/>
            <path fill-rule="evenodd" d="M13.854 2.146a.5.5 0 0 1 0 .708l-11 11a.5.5 0 0 1-.708-.708l11-11a.5.5 0 0 1 .708 0Z"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { state, socket } from "@/socket.js"

export default {
  name: 'UserControllPanel',
  components: {
  },
  data() {
    return {
      theme: localStorage.getItem("theme") || 'dark',
    }
  },
  // mounted() {
  //   // new Tooltip(document.body, {
  //   //   selector: "[data-bs-toggle='tooltip']",
  //   // });
  // },
  methods: {
    waitForMe: function(waitType) {
      if (waitType === 'skip') {
        if ( state.orderState === 'closed') {
          alert("A rendelés már el lett küldve.")
          return;
        }
        // Remove the basket cookie
        socket.emit("Server Basket Update", { "userid": state.user.id, "basket": {} });
      }
      socket.emit("User Daily State Change",{ 'id': state.user.id, 'new_state':waitType });
    },
    toggleDarkMode: function() {
      if (this.theme === 'dark') {
        this.theme = 'light'
      } else {
        this.theme = 'dark'
      }
      localStorage.setItem("theme", this.theme);
      socket.emit("User Update", {"id": state.user.id, "ui_theme":this.theme}, function(user) {
        state.user = user;
      });
      document.documentElement.setAttribute('data-bs-theme', this.theme)
    },
    subscribeToggle: function() {
      if (state.user.subscribed == "full") {
        socket.emit("User Update", {"id": state.user.id, "subscribed":"none"}, function(user) {
          state.user = user;
        });
      } else if (state.user.subscribed == "none") {
        socket.emit("User Update", {"id": state.user.id, "subscribed":"full"}, function(user) {
          state.user = user;
        });
      }
    }
  },
  computed: {
    isLoggedIn() {
      return state.user.id !== undefined;
    },
    currentUserState() {
      return state.userStates[state.user.username];
    },
    userColor() {
      return state.user.ui_color ? state.user.ui_color : "falusi";
    },
    subscriptionState() {
      return state.user.subscribed;
    }
  }
}
</script>

<style>
</style>
