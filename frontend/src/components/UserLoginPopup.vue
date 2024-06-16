<template>
  <Popup
    :show-modal="show"
    :title="showLogin ? 'Jelentkezz be!' : 'Regisztráció!'"
    :confirm-text="showLogin ? 'Belépés' : 'Regisztrál'"
    cancel-text="Mégse"
    @cancel="cancel()"
    @confirm="confirm()"
  >
    <p v-if="showLogin">Írd be a nevet amit regisztrációnál megadtál.</p>
    <p v-else>Válassz egy felhasználó nevet.</p>
    <p>{{ showLogin ? "Nincs fiókod?" : "Már van fiókod?"}}
      <a
        type="button"
        name="button"
        class="text-link"
        @click="change_login()"
      >
        {{ showLogin ? "Regisztrálj!" : "Jelentkezz be!"}}
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
  </Popup>
</template>

<script>
import Popup from './Popup.vue';
import { useAuth } from "@/stores/auth.js";

export default {
  name: 'UserLoginPopup',
  components: {
    Popup
  },
  props: {
    show: Boolean
  },
  emits: ['cancel', 'confirm'],
  setup() {
    const auth = useAuth();
    return {
      auth
    }
  },
  data() {
    return {
      username: "",
      showLogin: true
    }
  },
  mounted() {
    if (this.auth.isLoggedIn) {
      this.username = this.auth.user.username;
    }
  },
  methods: {
    login: function() {
      this.auth.login(this.username);
      this.$emit('cancel');
    },
    register: function() {
      this.auth.register(this.username);
      this.$emit('cancel');
    },
    change_login: function() {
      this.showLogin = !this.showLogin;
    },
    confirm: function() {
      if (this.showLogin) {
        this.login();
      } else {
        this.register();
      }
    },
    cancel: function() {
      this.showLogin = true;
      this.$emit('cancel');
    }
  }
}
</script>

<style>
</style>
