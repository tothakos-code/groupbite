<template>
  <div class="row ms-2">
    <div class="row">
      <h1 class="col">
        Vendor manager
      </h1>
      <div class="col">
        <div
          class="btn"
          :class="['btn-' + auth.userColor.value ]"
          @click="openAdminHome()"
        >
          vissza
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            fill="currentColor"
            class="bi bi-arrow-clockwise"
            viewBox="0 0 16 16"
          >
            <path
              fill-rule="evenodd"
              d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2z"
            />
            <path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466" />
          </svg>
        </div>
      </div>
    </div>
    <router-view />
  </div>
</template>

<script>
// import axios from 'axios';
import { useAuth } from '@/auth';

export default {
    name: 'AdminView',
    setup() {
      const auth = useAuth();
      return {
        auth
      }
    },
    data() {

    },
    mounted() {
    },
    methods: {
      openAdminHome: function () {
        this.$router.push({ path:`/admin`})
      }
    }
};
</script>

<style scoped>
</style>
