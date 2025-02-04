<template>
  <Popup
    :show-modal="show"
    :title="showRemainder ? 'Emlékeztető küldése' : showLogin ? 'Jelentkezz be!' : 'Regisztráció!'"
    :confirm-text="showRemainder ? 'Küldés' : showLogin ? 'Belépés' : 'Regisztrál'"
    cancel-text="Mégse"
    @cancel="cancel()"
    @confirm="confirm()"
  >
    <div
      v-if="!showRemainder"
      class=""
    >
      <div v-if="showLogin">
        <p>
          Írd be a nevet amit regisztrációnál megadtál.
        </p>
        <p>
          Nincs fiókod?

          <a
            type="button"
            name="button"
            class="text-link"
            @click="change_login()"
          >
            Regisztrálj!
          </a>
        </p>
        <div class="input-group mb-3">
          <span class="input-group-text">Név</span>
          <input
            v-model.trim="username"
            type="text"
            class="form-control"
            placeholder="Felhasználónév"
            aria-label="Username"
            aria-describedby="basic-addon1"
          >
        </div>
        <p>
          Elfelejtetted a bejelentkezési neved?
          <a
            type="button"
            name="button"
            class="text-link"
            @click="change_remainder()"
          >
            Emlékeztető email kérése
          </a>
        </p>
      </div>
      <div
        v-else
      >
        <p>
          Válassz egy felhasználó nevet.
        </p>
        <p>
          Már van fiókod?

          <a
            type="button"
            name="button"
            class="text-link"
            @click="change_login()"
          >
            Jelentkezz be!
          </a>
        </p>
        <div class="input-group mb-3">
          <span class="input-group-text">Név</span>
          <input
            v-model.trim="username"
            type="text"
            class="form-control"
            placeholder="Felhasználónév"
            aria-label="Username"
            aria-describedby="basic-addon1"
          >
        </div>
        <div
          class="input-group mb-3"
        >
          <span class="input-group-text">Email cím</span>
          <input
            v-model.trim="email"
            type="text"
            class="form-control"
            placeholder="Email cím"
            aria-label="Email"
            aria-describedby="basic-addon2"
          >
        </div>
      </div>
    </div>
    <div
      v-if="showRemainder"
      class=""
    >
      <p>
        Írd be a regisztrációkor megadott email címed amire elküldjük a bejelentkezési nevedet
      </p>
      <div
        class="input-group mb-3"
      >
        <span class="input-group-text">Email cím</span>
        <input
          v-model.trim="email"
          type="text"
          class="form-control"
          placeholder="Email cím"
          aria-label="Email"
          aria-describedby="basic-addon2"
        >
      </div>
      <p>
        <a
          type="button"
          name="button"
          class="text-link"
          @click="change_remainder()"
        >
          Vissza a bejelentkezéshez
        </a>
      </p>
    </div>
  </Popup>
</template>

<script>
import Popup from "./Popup.vue";
import { useAuth } from "@/stores/auth.js";

export default {
  name: "UserLoginPopup",
  components: {
    Popup
  },
  props: {
    show: Boolean
  },
  emits: ["cancel", "confirm"],
  setup() {
    const auth = useAuth();
    return {
      auth
    }
  },
  data() {
    return {
      username: "",
      email: "",
      showLogin: true,
      showRemainder: false
    }
  },
  mounted() {
    if (this.auth.isLoggedIn) {
      this.username = this.auth.user.username;
    }
  },
  methods: {
    login: function() {
      this.auth.login(this.username).then(response => {
        console.log(response);
        if (!response.data.error) {
          this.cancel()
        }
      })
    },
    register: function() {
      this.auth.register(this.username, this.email);
      this.$emit("cancel");
    },
    change_login: function() {
      this.showLogin = !this.showLogin;
    },
    change_remainder: function() {
      this.showRemainder = !this.showRemainder;
    },
    confirm: function() {
      if (this.showRemainder) {
        this.auth.sendReminder(this.email);
        return
      }
      if (this.showLogin) {
        this.login();
      } else {
        this.register();
      }
    },
    cancel: function() {
      this.showLogin = true;
      this.$emit("cancel");
    }
  }
}
</script>

<style>
</style>
