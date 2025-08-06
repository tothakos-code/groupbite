<template>
  <v-container
    fluid
    class="mb-6"
  >
    <!-- Statistics Cards Row -->
    <v-row class="mb-4">
      <v-col
        cols="12"
        md="4"
      >
        <v-card
          class="text-center pa-4"
          elevation="2"
        >
          <v-icon
            size="32"
            color="primary"
            class="mb-2"
          >
            mdi-receipt-text
          </v-icon>
          <h3 class="text-h6 font-weight-bold">
            {{ statistics.totalOrders }}
          </h3>
          <p class="text-body-2 grey--text mb-0">
            Összes rendelés
          </p>
        </v-card>
      </v-col>

      <v-col
        cols="12"
        md="4"
      >
        <v-card
          class="text-center pa-4"
          elevation="2"
        >
          <v-icon
            size="32"
            color="success"
            class="mb-2"
          >
            mdi-currency-usd
          </v-icon>
          <h3 class="text-h6 font-weight-bold">
            {{ (statistics.totalSpent).toFixed(2) }} Ft
          </h3>
          <p class="text-body-2 grey--text mb-0">
            Teljes költésed
          </p>
        </v-card>
      </v-col>

      <v-col
        cols="12"
        md="4"
      >
        <v-card
          class="text-center pa-4"
          elevation="2"
        >
          <v-icon
            size="32"
            color="info"
            class="mb-2"
          >
            mdi-calculator
          </v-icon>
          <h3 class="text-h6 font-weight-bold">
            {{ (statistics.averageOrderValue).toFixed(2) }} Ft
          </h3>
          <p class="text-body-2 grey--text mb-0">
            Rendeléseid átlaga
          </p>
        </v-card>
      </v-col>
    </v-row>

    <!-- Additional Statistics Row -->
    <v-row class="mb-4">
      <v-col
        cols="12"
        md="3"
      >
        <v-card
          class="text-center pa-4"
          elevation="2"
        >
          <v-icon
            size="32"
            color="orange"
            class="mb-2"
          >
            mdi-food
          </v-icon>
          <h3 class="text-h6 font-weight-bold">
            {{ statistics.totalItems }}
          </h3>
          <p class="text-body-2 grey--text mb-0">
            Rendelt tétel
          </p>
        </v-card>
      </v-col>

      <v-col
        cols="12"
        md="3"
      >
        <v-card
          class="text-center pa-4"
          elevation="2"
        >
          <v-icon
            size="32"
            color="purple"
            class="mb-2"
          >
            mdi-store
          </v-icon>
          <h3 class="text-h6 font-weight-bold">
            {{ statistics.uniqueVendors }}
          </h3>
          <p class="text-body-2 grey--text mb-0">
            Különböző üzlet
          </p>
        </v-card>
      </v-col>

      <v-col
        cols="12"
        md="3"
      >
        <v-card
          class="text-center pa-4"
          elevation="2"
        >
          <v-icon
            size="32"
            color="teal"
            class="mb-2"
          >
            mdi-heart
          </v-icon>
          <h3 class="text-h6 font-weight-bold">
            {{ statistics.favoriteVendor?.name || 'N/A' }}
          </h3>
          <p class="text-body-2 grey--text mb-0">
            Kedvenc üzleted
          </p>
        </v-card>
      </v-col>

      <v-col
        cols="12"
        md="3"
      >
        <v-card
          class="text-center pa-4"
          elevation="2"
        >
          <v-icon
            size="32"
            color="amber"
            class="mb-2"
          >
            mdi-star
          </v-icon>
          <h3 class="text-h6 font-weight-bold">
            {{ statistics.favoriteItem?.name || 'N/A' }}
          </h3>
          <p class="text-body-2 grey--text mb-0">
            Legtöbbet rendelt ételed
          </p>
        </v-card>
      </v-col>
    </v-row>

    <!-- Time-based Statistics -->
    <v-row class="mb-4">
      <v-col
        cols="12"
        md="4"
      >
        <v-card
          class="text-center pa-4"
          elevation="2"
        >
          <v-icon
            size="32"
            color="blue"
            class="mb-2"
          >
            mdi-calendar-month
          </v-icon>
          <h3 class="text-h6 font-weight-bold">
            {{ (statistics.thisMonthSpent).toFixed(2) }} Ft
          </h3>
          <p class="text-body-2 grey--text mb-0">
            A hónapban
          </p>
        </v-card>
      </v-col>

      <v-col
        cols="12"
        md="4"
      >
        <v-card
          class="text-center pa-4"
          elevation="2"
        >
          <v-icon
            size="32"
            color="green"
            class="mb-2"
          >
            mdi-calendar-week
          </v-icon>
          <h3 class="text-h6 font-weight-bold">
            {{ (statistics.thisWeekSpent).toFixed(2) }} Ft
          </h3>
          <p class="text-body-2 grey--text mb-0">
            Ezen a héten
          </p>
        </v-card>
      </v-col>

      <v-col
        cols="12"
        md="4"
      >
        <v-card
          class="text-center pa-4"
          elevation="2"
        >
          <v-icon
            size="32"
            color="red"
            class="mb-2"
          >
            mdi-calendar-today
          </v-icon>
          <h3 class="text-h6 font-weight-bold">
            {{ statistics.ordersThisMonth }}
          </h3>
          <p class="text-body-2 grey--text mb-0">
            Rendeléseid a hónapban
          </p>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, defineProps, onMounted } from 'vue'
import axios from "axios";

const props = defineProps({
  userId: {
    type: String,
    required: true
  }
})

const statistics = ref({
  totalOrders: 0,
  totalSpent: 0,
  totalItems: 0,
  uniqueVendors: 0,
  averageOrderValue: 0,
  favoriteVendor: null,
  favoriteItem: null,
  thisMonthSpent: 0,
  thisWeekSpent: 0,
  ordersThisMonth: 0
})

const loading = ref(true)

// Fetch statistics from API
const fetchStatistics = async () => {
  try {
    const response = await axios.get(`/api/user/${props.userId}/statistics`)

    statistics.value = response.data.statistics

    // Calculate average order value
    if (statistics.value.totalOrders > 0) {
      statistics.value.averageOrderValue = statistics.value.totalSpent / statistics.value.totalOrders
    }

  } catch (error) {
    console.error('Error fetching statistics:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStatistics()
})
</script>

<style scoped>
.v-card {
  transition: transform 0.2s ease-in-out;
}

.v-card:hover {
  transform: translateY(-2px);
}

.text-h6 {
  line-height: 1.2;
}

.grey--text {
  color: rgba(0, 0, 0, 0.6) !important;
}
</style>
