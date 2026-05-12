<template>
  <div class="current-user-basket">
    <!-- Current User Header -->
    <div class="user-header bg-success-lighten-5 px-4 py-3">
      <v-row
        align="center"
        no-gutters
      >
        <v-col cols="auto">
          <v-avatar
            size="32"
            color="success"
          >
            <v-icon>mdi-account</v-icon>
          </v-avatar>
        </v-col>
        <v-col class="ms-3">
          <h3 class="text-h6 font-weight-bold text-success-darken-2">
            Saját kosarad
          </h3>
        </v-col>
        <v-col cols="auto">
          <v-tooltip
            open-on-hover
            open-on-click
            open-delay="500"
            max-width="280"
            location="top"
          >
            <template #activator="{ props: activatorProps }">
              <div
                v-bind="activatorProps"
                class="d-flex align-center"
              >
                <v-icon
                  class="me-1"
                  color="success"
                >
                  mdi-cash
                </v-icon>
                <span class="text-h6 font-weight-bold text-success-darken-2">
                  {{ userBasketSum }} Ft
                </span>
              </div>
            </template>

            <div>
              A fizetendő összeg még változhat a rendelést leadó személyek számától.
              (Szállítási díjat több felé osztjuk)
            </div>
          </v-tooltip>
        </v-col>
        <v-col
          v-if="!isEmpty"
          cols="auto"
          class="ms-2"
        >
          <v-tooltip
            open-on-hover
            open-on-click
            open-delay="500"
            max-width="280"
            location="top"
          >
            <template #activator="{ props: activatorProps }">
              <v-btn
                v-bind="activatorProps"
                variant="outlined"
                color="error"
                size="small"
                @click="emit('clear-basket')"
              >
                <v-icon class="me-1">
                  mdi-delete
                </v-icon>
                <span class="d-none d-sm-inline">Törlés</span>
              </v-btn>
            </template>
            <span>Töröl mindent a kosaradból</span>
          </v-tooltip>
        </v-col>
      </v-row>
    </div>

    <!-- Current User Items -->
    <div class="user-items">
      <v-list
        v-if="!isEmpty"
        density="comfortable"
      >
        <v-list-item
          v-for="(item, idx) in userBasket"
          :key="`${item.item_id}-${item.size_id || 'default'}-${idx}`"
          class="basket-item"
        >
          <template #prepend>
            <v-chip
              :class="{ 'animate-pulse': itemQuantityPulse }"
              color="secondary"
              size="small"
              variant="elevated"
              @animationend="itemQuantityPulse = false"
            >
              {{ item.quantity }}x
            </v-chip>
          </template>

          <v-tooltip
            open-on-hover
            open-on-click
            open-delay="500"
            max-width="280"
            location="top"
          >
            <template #activator="{ props: activatorProps }">
              <v-list-item-title
                v-bind="activatorProps"
                class="text-truncate"
              >
                {{ item.item_name }}
                <span
                  v-if="item.size_name"
                  class="text-caption text-medium-emphasis"
                >
                  ({{ item.size_name }})
                </span>
              </v-list-item-title>
            </template>
            <div>
              {{ item.item_name }}
              <span v-if="item.size_name">({{ item.size_name }})</span>
            </div>
          </v-tooltip>

          <!-- Option selections: live data or snapshot fallback -->
          <v-list-item-subtitle
            v-if="(item.option_selections && item.option_selections.length) || item.extras_summary?.options?.length"
            class="text-caption text-medium-emphasis mt-1"
          >
            {{ (item.option_selections?.length ? item.option_selections : item.extras_summary?.options || []).map(s => s.choice).join(', ') }}
          </v-list-item-subtitle>

          <!-- Bundle discount badge: live data or snapshot fallback -->
          <v-chip
            v-if="item.bundle_discount || item.extras_summary?.bundle"
            size="x-small"
            color="success"
            variant="tonal"
            prepend-icon="mdi-sale"
            class="mt-1"
          >
            {{ (item.bundle_discount || item.extras_summary?.bundle).name }}
            <template v-if="(item.bundle_discount || item.extras_summary?.bundle).applied_delta">
              : {{ formatDelta((item.bundle_discount || item.extras_summary?.bundle).applied_delta) }}
            </template>
          </v-chip>

          <template #append>
            <div class="d-flex align-center">
              <div class="text-end me-1">
                <div
                  v-if="item.bundle_discount || item.extras_summary?.bundle"
                  class="text-caption text-medium-emphasis text-decoration-line-through"
                >
                  {{ (item.bundle_discount || item.extras_summary?.bundle).original_price }} Ft
                </div>
                <span
                  class="text-h6 font-weight-bold"
                  :class="(item.bundle_discount || item.extras_summary?.bundle) ? 'text-success' : ''"
                >
                  {{ item.effective_price ?? item.price }} Ft
                </span>
              </div>
              <v-btn
                variant="text"
                color="error"
                size="small"
                icon="mdi-close"
                @click="emit('remove-item', item.item_id, item.size_id, item.option_choice_ids || [])"
              />
            </div>
          </template>
        </v-list-item>
      </v-list>

      <!-- Empty State -->
      <div
        v-else
        class="empty-basket text-center py-8"
      >
        <v-icon
          size="64"
          color="grey-lighten-2"
        >
          mdi-basket-outline
        </v-icon>
        <p class="text-h6 text-grey-lighten-1 mt-3">
          Üres a kosarad
        </p>
        <p class="text-body-2 text-grey">
          Válassz ételt a menüből!
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

// Props
const props = defineProps({
  userBasket: {
    type: Object,
    required: true
  },
  userBasketSum: {
    type: Number,
    required: true
  },
  transportFee: {
    type: Number,
    default: 0
  },
  isEmpty: {
    type: Boolean,
    required: true
  }
})

// Emits
const emit = defineEmits(['clear-basket', 'remove-item'])

// Reactive data
const itemQuantityPulse = ref(false)

// Watch for basket changes to trigger animation
watch(() => props.userBasket, () => {
  itemQuantityPulse.value = true
}, { deep: true })

function formatDelta(delta) {
  if (!delta) return ''
  const sign = delta > 0 ? '+' : ''
  return `${sign}${delta} Ft`
}
</script>

<style scoped>
.current-user-basket {
  border-bottom: 2px solid rgb(var(--v-theme-success));
}

.user-header {
  border-left: 4px solid rgb(var(--v-theme-success));
}

.basket-item {
  border-bottom: 1px solid rgb(var(--v-theme-outline-variant));
}

.basket-item:hover {
  background-color: rgb(var(--v-theme-secondary));
}

.animate-pulse {
  animation: pulse 0.5s ease-in-out;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

.empty-basket {
  background-color: rgb(var(--v-theme-surface));
  border: 1px solid rgb(var(--v-theme-outline-variant));
  border-radius: 8px;
  margin: 16px;
}



</style>
