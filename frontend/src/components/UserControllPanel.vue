<template>
  <div class="ms-2 ms-md-0 d-flex justify-content-start">
    <div class="col my-auto">
      <button
        class="btn"
        :class="{
          'btn-dark':theme === 'light',
          'btn-light':theme === 'dark'
        }"
        @click="toggleDarkMode"
      >
        <svg
          v-if="theme === 'light'"
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          fill="currentColor"
          class="bi bi-moon-fill"
          viewBox="0 0 16 16"
        >
          <path d="M6 .278a.768.768 0 0 1 .08.858 7.208 7.208 0 0 0-.878 3.46c0 4.021 3.278 7.277 7.318 7.277.527 0 1.04-.055 1.533-.16a.787.787 0 0 1 .81.316.733.733 0 0 1-.031.893A8.349 8.349 0 0 1 8.344 16C3.734 16 0 12.286 0 7.71 0 4.266 2.114 1.312 5.124.06A.752.752 0 0 1 6 .278z" />
        </svg>
        <svg
          v-else
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          fill="currentColor"
          class="bi bi-brightness-high-fill"
          viewBox="0 0 16 16"
        >
          <path d="M12 8a4 4 0 1 1-8 0 4 4 0 0 1 8 0zM8 0a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 0zm0 13a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 13zm8-5a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2a.5.5 0 0 1 .5.5zM3 8a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2A.5.5 0 0 1 3 8zm10.657-5.657a.5.5 0 0 1 0 .707l-1.414 1.415a.5.5 0 1 1-.707-.708l1.414-1.414a.5.5 0 0 1 .707 0zm-9.193 9.193a.5.5 0 0 1 0 .707L3.05 13.657a.5.5 0 0 1-.707-.707l1.414-1.414a.5.5 0 0 1 .707 0zm9.193 2.121a.5.5 0 0 1-.707 0l-1.414-1.414a.5.5 0 0 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .707zM4.464 4.465a.5.5 0 0 1-.707 0L2.343 3.05a.5.5 0 1 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .708z" />
        </svg>
      </button>
    </div>
    <div
      v-if="auth.isLoggedIn"
      class="col"
    >
      <button
        type="button"
        class="btn ms-2 position-relative"
        :class="['btn-' + auth.userColor.value ]"
        title="Ha feliratkozol megjelenik a neved minden nap a közös kosárban. Így a többiek látják, hogy még nem választottál és biztos nem maradsz le a rendelésről. Akkor érdemes feliratkozni, ha nagyon sokszor rendelsz a falusiból."
        @click="subscribeToggle()"
      >
        <div
          v-if="subscriptionState != 'full'"
          class="text-nowrap"
        >
          <span class="d-none d-lg-inline me-1">Feliratkozás</span>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            fill="currentColor"
            class="bi bi-arrow-repeat"
            viewBox="0 0 16 16"
          >
            <path d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z" />
            <path
              fill-rule="evenodd"
              d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5.002 5.002 0 0 0 8 3zM3.1 9a5.002 5.002 0 0 0 8.757 2.182.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9H3.1z"
            />
          </svg>
          <span class="position-absolute top-0 start-50 translate-middle badge rounded-pill bg-danger">
            <span class="d-none d-lg-inline">Leiratkozva</span>
          </span>
        </div>
        <div
          v-else
          class="text-nowrap"
        >
          <span class="d-none d-lg-inline me-1">Leiratkozás</span>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            fill="currentColor"
            class="bi bi-arrow-repeat"
            viewBox="0 0 16 16"
          >
            <path d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z" />
            <path
              fill-rule="evenodd"
              d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5.002 5.002 0 0 0 8 3zM3.1 9a5.002 5.002 0 0 0 8.757 2.182.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9H3.1z"
            />
            <path
              fill-rule="evenodd"
              d="M13.854 2.146a.5.5 0 0 1 0 .708l-11 11a.5.5 0 0 1-.708-.708l11-11a.5.5 0 0 1 .708 0Z"
            />
          </svg>
          <span class="position-absolute top-0 start-50 translate-middle badge rounded-pill bg-success">
            <span class="d-none d-lg-inline">Feliratkozva</span>
          </span>
        </div>
      </button>
    </div>
  </div>
</template>

<script>
import { state, socket } from "@/socket.js";
import { useAuth } from "@/auth.js";
import { inject } from 'vue';

export default {
  name: 'UserControllPanel',
  setup() {
    const { theme, toggleDarkMode } = inject('theme')
    const auth = useAuth();

    return {
      theme,
      auth,
      toggleDarkMode
    }
  },
  computed: {
    currentUserState() {
      return state.userStates[state.user.username];
    },
    subscriptionState() {
      return state.user.subscribed;
    }
  },
  methods: {
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
  }
}
</script>

<style>
</style>
