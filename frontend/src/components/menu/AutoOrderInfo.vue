<template>
  <div class="d-flex align-items-center gap-2">
    <v-tooltip location="bottom">
      <template #activator="{ props }">
        <span
          v-bind="props"
          class="text-button font-weight-bold"
        >
          Határidő: {{ deadline }}
        </span>
      </template>
      <span>Az automata rendelés be van kapcsolva ennél az étkezdénél</span>
    </v-tooltip>

    <v-tooltip location="bottom">
      <template #activator="{ props }">
        <v-icon
          v-bind="props"
          :color="isConditionMet ? 'success' : 'warning'"
          :icon="isConditionMet ? 'mdi-clock-check-outline' : 'mdi-clock-alert-outline'"
        />
      </template>
      <span>
        Az automata rendelés feltétele {{ isConditionMet ? 'teljesült' : 'NEM teljesül' }}.
        Min {{ currentUsers }}/{{ minUsers }} rendelő
      </span>
    </v-tooltip>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  deadline: {
    type: String,
    required: true
  },
  minUsers: {
    type: Number,
    required: true
  },
  currentUsers: {
    type: Number,
    required: true
  }
})

const isConditionMet = computed(() => props.currentUsers >= props.minUsers)
</script>
