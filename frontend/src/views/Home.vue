<template>
  <div>
    <h1>Home</h1>
  </div>
  <History />
</template>

<script>
import History from '@/components/History.vue'
export default {
    name: 'HomeView',
    components: {
      History,
    }
};
</script>

<style scoped>
</style>
