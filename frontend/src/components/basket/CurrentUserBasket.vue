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
          <v-tooltip location="bottom">
            <template #activator="{ p }">
              <div
                v-bind="p"
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
            <span>
              A fizetendő összeg még változhat a rendelést leadó személyek számától.
              (Szállítási díjat több felé osztjuk)
            </span>
          </v-tooltip>
        </v-col>
        <v-col
          v-if="!isEmpty"
          cols="auto"
          class="ms-2"
        >
          <v-tooltip location="bottom">
            <template #activator="{ p }">
              <v-btn
                v-bind="p"
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
          v-for="item in userBasket"
          :key="`${item.item_id}-${item.size_id || 'default'}`"
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

          <v-list-item-title class="font-weight-medium">
            {{ item.item_name }}
            <span
              v-if="item.size_name"
              class="text-medium-emphasis"
            >
              ({{ item.size_name }})
            </span>
          </v-list-item-title>

          <template #append>
            <div class="d-flex align-center">
              <span class="text-h6 font-weight-bold me-3">
                {{ item.price }} Ft
              </span>
              <v-btn
                variant="text"
                color="error"
                size="small"
                icon="mdi-close"
                @click="emit('remove-item', item.item_id, item.size_id)"
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
