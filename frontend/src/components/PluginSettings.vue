<template>
  <div class="row ms-2">
    <div class="">
      <h1 class="">
        Plugin Config {{ $route.params.id }}
      </h1>
    </div>
  </div>
</template>

<script>
// import axios from 'axios';
import { useAuth } from '@/auth';

export default {
    name: 'PluginConfiguration',
    setup() {
      const auth = useAuth();
      return {
        auth
      }
    },
    data() {
      return {}
    },
    mounted() {
    },
    methods: {
    }
};
</script>

<style scoped>
</style>
