<template>
  <div class="d-flex p-2">
    <div class="row-12 mb-2">
      <WeekSummary />
    </div>
    <div class="row-12 mb-2">
      <WeekGraph />
    </div>
  </div>
</template>

<script>
import { defineAsyncComponent } from 'vue'
const WeekSummary = defineAsyncComponent(() => import("@/components/WeekSummary.vue"));
const WeekGraph = defineAsyncComponent(() => import("@/components/WeekGraph.vue"));

export default {
    name: "HomeView",
    components: {
      WeekSummary,
      WeekGraph
    }
};
</script>

<style scoped>
</style>
