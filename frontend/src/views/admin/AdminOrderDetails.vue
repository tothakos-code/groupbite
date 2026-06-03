<template>
  <v-container
    fluid
    class="pa-2 pa-md-4"
  >
    <v-btn
      color="primary"
      variant="outlined"
      size="small"
      class="mb-4"
      @click="router.back()"
    >
      <v-icon start>
        mdi-arrow-left
      </v-icon>
      Vissza a rendelésekhez
    </v-btn>

    <!-- Loading skeleton -->
    <template v-if="isLoading">
      <v-skeleton-loader
        type="card"
        class="mb-4"
      />
      <v-skeleton-loader type="article" />
    </template>

    <!-- Error alert -->
    <v-alert
      v-else-if="error"
      type="error"
      class="mb-4"
    >
      {{ error }}
    </v-alert>

    <template v-else>
      <!-- Order metadata card -->
      <v-card
        class="mb-4"
        elevation="2"
      >
        <v-card-title class="pb-1">
          #{{ order.id }} – {{ order.vendor }}
        </v-card-title>
        <v-card-text>
          <v-row dense>
            <v-col
              cols="12"
              sm="auto"
              class="me-4"
            >
              <span class="text-caption text-medium-emphasis">Dátum: </span>
              {{ formatDate(order.open_from) }}
            </v-col>
            <v-col
              cols="12"
              sm="auto"
              class="me-4"
            >
              <span class="text-caption text-medium-emphasis">Állapot: </span>
              <v-chip
                :color="getStatusColor(order.state_id)"
                size="small"
                variant="flat"
                class="ml-1"
              >
                {{ order.state_id }}
              </v-chip>
            </v-col>
            <v-col
              cols="12"
              sm="auto"
            >
              <span class="text-caption text-medium-emphasis">Rendelési díj: </span>
              {{ order.order_fee }} Ft
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- Per-user baskets -->
      <div
        v-if="basketEntries.length === 0"
        class="text-center py-6 text-medium-emphasis"
      >
        Nincs kosár adat ehhez a rendeléshez.
      </div>
      <UserBasket
        v-for="entry in basketEntries"
        :key="entry.user_id"
        :username="entry.username"
        :user-id="entry.user_id"
        :user-basket="entry.items"
        :transport-fee="0"
        :copyable="false"
        :initially-expanded="true"
      />
    </template>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import UserBasket from '@/components/basket/UserBasket.vue'

const route = useRoute()
const router = useRouter()

const order = ref(null)
const basket = ref({})
const isLoading = ref(true)
const error = ref(null)

const basketEntries = computed(() => Object.values(basket.value))

const getStatusColor = (status) => {
  switch (status) {
    case 'collect': return 'success'
    case 'order': return 'warning'
    case 'closed': return 'error'
    default: return 'default'
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('hu-HU', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

onMounted(async () => {
  try {
    const response = await axios.get(`/api/order/${route.params.orderId}`)
    const data = response.data.data
    order.value = data
    basket.value = data.basket ?? {}
  } catch (err) {
    if (err.response?.status === 404) {
      error.value = 'A rendelés nem található.'
    } else {
      error.value = 'Hiba történt az adatok betöltése során.'
    }
  } finally {
    isLoading.value = false
  }
})
</script>
