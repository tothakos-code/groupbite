<template>
  <v-chip
    :color="statusColor"
    :title="statusTitle"
    class="px-3 py-2"
    size="default"
    variant="elevated"
  >
    <v-icon
      v-if="statusIcon"
      :icon="statusIcon"
      start
      size="small"
    />
    {{ statusLabel }}
  </v-chip>
</template>

<script setup>
import { computed } from 'vue'
import { state } from '@/main'
import { useOrderStore } from '@/stores/order'

// Composables
const orderStore = useOrderStore()

// Order state configuration
const ORDER_STATES = {
  collect: {
    label: 'Rendelhetsz',
    color: 'success',
    icon: 'mdi-check-circle',
    title: 'Rendelést még nem küldték el, nyugodtan csatlakozhatsz hozzá.'
  },
  order: {
    label: 'Siess!',
    color: 'warning',
    icon: 'mdi-clock-alert',
    title: 'A rendelés éppen küldés alatt van, ha szeretnél még csatlakozni hozzá SIESS!'
  },
  closed: {
    label: 'Rendelés elküldve',
    color: 'error',
    icon: 'mdi-lock',
    title: 'Rendelés elküldve. Sajnos lemaradtál a rendelésről vagy, ha már rendeltél akkor biztosan jól fogsz lakni.'
  }
}

const CONNECTION_ERROR_STATE = {
  label: 'Kapcsolati probléma',
  color: 'error',
  icon: 'mdi-wifi-off',
  title: 'Sajnos nem sikerül csatlakozni a szerverhez.'
}

const DEFAULT_STATE = {
  label: 'Töltés...',
  color: 'secondary',
  icon: 'mdi-loading',
  title: 'Sajnos valami probléma merült fel a szerveren.'
}

// Computed properties
const currentState = computed(() => {
  if (!state.connected) {
    return CONNECTION_ERROR_STATE
  }

  const stateId = orderStore.order.state_id
  return ORDER_STATES[stateId] || DEFAULT_STATE
})

const statusLabel = computed(() => currentState.value.label)
const statusColor = computed(() => currentState.value.color)
const statusIcon = computed(() => currentState.value.icon)
const statusTitle = computed(() => currentState.value.title)
</script>
