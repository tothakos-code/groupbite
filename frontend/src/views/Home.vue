<template>
  <div class="d-flex p-2">
    <div class="row-12 mb-2">
      <WeekSummary />
    </div>
    <div class="row-12 mb-2">
      <div class="card">
        <div class="card-header">
          asd
        </div>
        <div class="card-body">
          ad
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import WeekSummary from '@/components/WeekSummary.vue'
export default {
    name: 'HomeView',
    components: {
      WeekSummary,
    }
};
</script>

<style scoped>
</style>
