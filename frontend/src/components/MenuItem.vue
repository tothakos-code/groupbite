<template>
  <v-card
    class="menu-item-card mb-3"
    elevation="2"
    rounded="lg"
  >
    <v-card-text class="pa-4">
      <!-- Item Header -->
      <div class="item-header mb-3">
        <div class="d-flex align-center justify-space-between">
          <div class="item-info flex-grow-1">
            <h3 class="text-h6 font-weight-bold text-primary mb-1">
              {{ item.name }}
            </h3>
            <p
              v-if="item.description"
              class="text-body-2 text-medium-emphasis ma-0"
            >
              {{ item.description }}
            </p>
          </div>
          <v-chip
            v-if="item.category"
            size="small"
            variant="tonal"
            color="primary"
            class="ms-2"
          >
            <v-icon
              start
              size="x-small"
            >
              {{ getCategoryIcon(item.category) }}
            </v-icon>
            {{ item.category }}
          </v-chip>
        </div>
      </div>

      <!-- Size Options -->
      <div class="size-options">
        <v-row class="ma-0">
          <v-col
            v-for="size in item.sizes"
            :key="size.id"
            cols="12"
            sm="6"
            md="4"
            lg="3"
            class="pa-1"
          >
            <v-card
              :class="[
                'size-card',
                size.unlimited || size.quantity > 0 ? 'available' : 'unavailable'
              ]"
              :elevation="size.unlimited || size.quantity > 0 ? 2 : 0"
              rounded="lg"
            >
              <v-card-text class="pa-3">
                <div class="size-info mb-2">
                  <div class="d-flex align-center justify-space-between mb-1">
                    <span class="text-subtitle-2 font-weight-bold">
                      {{ size.name }}
                    </span>
                    <v-chip
                      v-if="!size.unlimited && size.quantity <= 5 && size.quantity > 0"
                      size="x-small"
                      color="warning"
                      variant="flat"
                    >
                      {{ size.quantity }} db
                    </v-chip>
                  </div>
                  <div class="price-display">
                    <span class="text-h6 font-weight-bold text-primary">
                      {{ formatPrice(size.price) }}
                    </span>
                  </div>
                </div>

                <!-- Action Button -->
                <v-btn
                  v-if="size.unlimited || size.quantity > 0"
                  block
                  color="primary"
                  variant="elevated"
                  class="order-btn"
                  @click="handleOrder(item.id, size.id)"
                >
                  <v-icon
                    start
                    size="small"
                  >
                    mdi-plus-circle
                  </v-icon>
                  Rendelés
                </v-btn>

                <v-btn
                  v-else
                  block
                  color="error"
                  variant="tonal"
                  disabled
                  class="sold-out-btn"
                >
                  <v-icon
                    start
                    size="small"
                  >
                    mdi-close-circle
                  </v-icon>
                  Elfogyott
                </v-btn>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </div>

      <!-- Additional Info -->
      <div
        v-if="item.allergens || item.nutritionalInfo"
        class="additional-info mt-3 pt-3"
      >
        <v-divider class="mb-3" />
        <div class="d-flex flex-wrap gap-2">
          <v-chip
            v-if="item.allergens"
            size="small"
            variant="outlined"
            color="warning"
            prepend-icon="mdi-alert-circle"
          >
            Allergének: {{ item.allergens }}
          </v-chip>
          <v-chip
            v-if="item.nutritionalInfo"
            size="small"
            variant="outlined"
            color="info"
            prepend-icon="mdi-information"
          >
            {{ item.nutritionalInfo }}
          </v-chip>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script>
import { useAuth } from "@/stores/auth";
import { useOrderStore } from "@/stores/order";

export default {
  name: "MenuItem",
  props: {
    item: {
      type: Object,
      required: true,
      default: () => ({})
    },
  },
  setup() {
    const auth = useAuth();
    const order = useOrderStore();
    return {
      auth,
      order
    }
  },
  methods: {
    handleOrder(itemId, sizeId) {
      this.order.addItem(itemId, sizeId);

      // Optional: Show a brief success feedback
      this.$emit('item-added', { itemId, sizeId });
    },

    formatPrice(price) {
      return new Intl.NumberFormat('hu-HU', {
        style: 'currency',
        currency: 'HUF',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      }).format(price);
    },

    getCategoryIcon(category) {
      const iconMap = {
        'leves': 'mdi-bowl-mix',
        'főétel': 'mdi-food-steak',
        'desszert': 'mdi-cupcake',
        'ital': 'mdi-cup',
        'saláta': 'mdi-leaf',
        'pizza': 'mdi-pizza',
        'hamburger': 'mdi-hamburger',
        'tészta': 'mdi-pasta'
      };
      return iconMap[category.toLowerCase()] || 'mdi-food';
    }
  }
}
</script>

<style scoped>
.menu-item-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgb(var(--v-theme-outline));
  background: rgb(var(--v-theme-surface));
}

.menu-item-card:hover {
  box-shadow: 0 8px 25px rgba(var(--v-theme-shadow), 0.15);
}

.item-header {
  border-bottom: 2px solid rgba(var(--v-theme-primary), 0.2);
  padding-bottom: 12px;
}

.size-card {
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.size-card.available {
  background: rgb(var(--v-theme-surface-container-high));
  border-color: rgba(var(--v-theme-primary), 0.2);
}

.size-card.available:hover {
  transform: translateY(-2px);
  border-color: rgba(var(--v-theme-primary), 0.4);
  box-shadow: 0 4px 12px rgba(var(--v-theme-primary), 0.15);
}

.size-card.unavailable {
  background: rgb(var(--v-theme-surface-variant));
  border-color: rgb(var(--v-theme-outline));
  opacity: 0.6;
}

.price-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.order-btn {
  font-weight: 600;
  text-transform: none;
  letter-spacing: 0.5px;
}

.sold-out-btn {
  font-weight: 500;
  text-transform: none;
  opacity: 0.7;
}

.additional-info {
  border-top: 1px solid rgb(var(--v-theme-outline));
}

.gap-2 {
  gap: 8px;
}

/* Dark theme specific adjustments */
.v-theme--dark .menu-item-card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.v-theme--dark .menu-item-card:hover {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
}

.v-theme--dark .size-card.available {
  background: rgba(var(--v-theme-primary), 0.1);
}

.v-theme--dark .size-card.unavailable {
  background: rgba(var(--v-theme-surface), 0.5);
}

/* Responsive adjustments */
@media (max-width: 960px) {
  .item-info {
    margin-bottom: 8px;
  }

  .size-card {
    margin-bottom: 8px;
  }
}

@media (max-width: 600px) {
  .menu-item-card {
    margin-bottom: 16px;
  }

  .item-header {
    flex-direction: column;
    align-items: flex-start !important;
  }

  .item-header .v-chip {
    margin-top: 8px;
    margin-left: 0 !important;
  }
}

/* Animation for quantity chips */
.v-chip {
  transition: all 0.2s ease;
}

.v-chip:hover {
  transform: scale(1.05);
}
</style>
