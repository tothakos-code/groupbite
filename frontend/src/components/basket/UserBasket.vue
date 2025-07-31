<template>
  <v-expansion-panels
    v-model="expanded"
    variant="accordion"
    class="compact-user-basket mb-1"
    bg-color="surface"
  >
    <v-expansion-panel class="user-panel">
      <v-expansion-panel-title class="user-panel-header pa-3 border-bottom">
        <v-row
          align="center"
          no-gutters
        >
          <v-col cols="auto">
            <v-avatar
              size="28"
              color="primary"
              class="me-3"
            >
              <span class="text-caption font-weight-bold">
                {{ username.charAt(0).toUpperCase() }}
              </span>
            </v-avatar>
          </v-col>
          <v-col>
            <div class="text-subtitle-1 font-weight-medium text-truncate">
              {{ username }}
            </div>
            <div class="text-caption text-medium-emphasis">
              {{ itemCount }} tétel
            </div>
          </v-col>
          <v-col
            cols="auto"
            class="me-4"
          >
            <div class="text-end">
              <div class="text-h6 font-weight-bold">
                {{ basketTotal }} Ft
              </div>
            </div>
          </v-col>
          <v-col
            v-if="copyable"
            cols="auto"
            class="me-2"
          >
            <v-tooltip location="bottom">
              <template #activator="{ p }">
                <v-btn
                  v-bind="p"
                  variant="outlined"
                  color="primary"
                  size="small"
                  icon="mdi-content-copy"
                  @click.stop="emit('copy-basket', userId)"
                />
              </template>
              <span>Kosár másolása</span>
            </v-tooltip>
          </v-col>
        </v-row>
      </v-expansion-panel-title>

      <v-expansion-panel-text class="pa-0 user-panel">
        <v-list
          density="compact"
          class="bg-surface user-panel"
        >
          <v-list-item
            v-for="item in userBasketArray"
            :key="`${item.item_id}-${item.size_id || 'default'}`"
            class="compact-item px-4 py-2"
          >
            <template #prepend>
              <v-chip
                color="secondary"
                size="x-small"
                variant="flat"
                class="me-3"
              >
                {{ item.quantity }}x
              </v-chip>
            </template>

            <v-list-item-title class="text-body-2">
              {{ item.item_name }}
              <span
                v-if="item.size_name"
                class="text-caption text-medium-emphasis"
              >
                ({{ item.size_name }})
              </span>
            </v-list-item-title>

            <template #append>
              <span class="text-body-2 font-weight-medium">
                {{ item.price }} Ft
              </span>
            </template>
          </v-list-item>

          <!-- Transport fee info -->
          <v-divider />
          <v-list-item class="px-4 py-2 bg-surface">
            <v-list-item-title class="text-caption text-medium-emphasis">
              Szállítási díj: {{ Math.ceil(transportFee) }} Ft
            </v-list-item-title>
            <template #append>
              <span class="text-caption font-weight-medium">
                Összesen: {{ basketTotal }} Ft
              </span>
            </template>
          </v-list-item>
        </v-list>
      </v-expansion-panel-text>
    </v-expansion-panel>
  </v-expansion-panels>
</template>

<script setup>
import { computed, ref } from 'vue'

// Props
const props = defineProps({
  username: {
    type: String,
    required: true
  },
  userId: {
    type: String,
    required: true
  },
  userBasket: {
    type: Object,
    required: true
  },
  transportFee: {
    type: Number,
    default: 0
  },
  copyable: {
    type: Boolean,
    default: true
  },
  initiallyExpanded: {
    type: Boolean,
    default: true
  }
})

// Emits
const emit = defineEmits(['copy-basket'])

// Reactive data
const expanded = ref(props.initiallyExpanded ? [0] : [])

// Methods exposed to parent
const expand = () => {
  expanded.value = [0]
}

const collapse = () => {
  expanded.value = []
}

// Expose methods to parent component
defineExpose({
  expand,
  collapse
})

// Computed properties
const userBasketArray = computed(() => {
  return Object.values(props.userBasket)
})

const itemCount = computed(() => {
  return userBasketArray.value.reduce((total, item) => total + Number(item.quantity), 0)
})

const basketTotal = computed(() => {
  let sum = 0
  userBasketArray.value.forEach((entry) => {
    sum += Number(entry.quantity) * Number(entry.price)
  })
  sum += Math.ceil(props.transportFee)
  return sum
})
</script>

<style scoped>
.user-panel {
  border-radius: 12px !important;
}


.compact-user-basket {
  margin: 0 8px;
}

.user-panel-header {
  background-color: rgb(var(--v-theme-surface)) !important;
  min-height: 64px !important;
  border: 1px solid rgb(var(--v-theme-outline-variant));
  border-radius: 12px !important;
}

.compact-item {
  border-bottom: 1px solid rgb(var(--v-theme-outline-variant));
  background-color: rgb(var(--v-theme-surface));
}

.compact-item:last-child {
  border-bottom: none;
}

.compact-item:hover {
  background-color: rgb(var(--v-theme-secondary));
}

:deep(.v-expansion-panel) {
  background-color: rgb(var(--v-theme-surface)) !important;
}

:deep(.v-expansion-panel-title) {
  padding: 12px 16px;
  background-color: rgb(var(--v-theme-surface)) !important;
}

:deep(.v-expansion-panel-title__overlay) {
  background-color: transparent;
}

:deep(.v-expansion-panel-text__wrapper) {
  padding: 0;
  border-radius: 12px !important;
  background-color: rgb(var(--v-theme-surface)) !important;
}

:deep(.v-expansion-panel-text) {
  background-color: rgb(var(--v-theme-surface)) !important;
}
</style>
