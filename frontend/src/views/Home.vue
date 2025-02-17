<template>
  <v-row class="  d-flex m-2 pt-2">
    <v-col
      cols="12"
    >
      <v-row class=" mb-2">
        <v-col
          cols="12"
          md="8"
        >
          <WeekSummary />
        </v-col>
        <v-col
          cols="12"
          md="4"
        >
          <OrderSplitter />
        </v-col>
      </v-row>
      <!-- <v-row class="mb-2 d-block d-md-none">
      </v-row> -->
      <v-row class=" mb-2">
        <v-col cols="12">
          <WeekGraph />
        </v-col>
      </v-row>
    </v-col>

    <!-- <v-col
      cols="4"
      class="d-none d-md-block"
    >
      <OrderSplitter />
    </v-col> -->
  </v-row>
</template>

<script>
import { defineAsyncComponent } from 'vue'
const WeekSummary = defineAsyncComponent(() => import("@/components/WeekSummary.vue"));
const WeekGraph = defineAsyncComponent(() => import("@/components/WeekGraph.vue"));
const OrderSplitter = defineAsyncComponent(() => import("@/components/OrderSplitter.vue"));

export default {
    name: "HomeView",
    components: {
      WeekSummary,
      WeekGraph,
      OrderSplitter
    }
};
</script>

<style scoped>
</style>
