<template>
  <div class="row ms-2">
    <div class="">
      <h1 class="">
        A keresett útvonal nem található
      </h1>
      <button
        class="btn "
        :class="['btn-' + auth.getUserColor ]"
        title="Home"
        @click="openHome()"
      >
        <span class="text fs-4 text-center text-truncate m-auto">
          Vissza
        </span>
      </button>
    </div>
  </div>
</template>

<script>
import { useAuth } from "@/stores/auth";

export default {
    name: "NotFound",
    setup() {
      const auth = useAuth();
      return {
        auth
      }
    },
    methods: {
      openHome: function() {
        this.$router.push({ path:`/home`})
      }
    }
};
</script>

<style scoped>
</style>
