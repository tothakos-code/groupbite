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
          <v-btn
            v-if="auth.isLoggedIn"
            :icon="isFavourite ? 'mdi-star' : 'mdi-star-outline'"
            :color="isFavourite ? 'warning' : 'default'"
            variant="text"
            size="small"
            class="ms-1"
            @click.stop="toggleFavourite"
          />
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
        <div class="size-grid">
          <div
            v-for="size in item.sizes"
            :key="size.id"
            class="size-item"
          >
            <v-card
              :class="[
                'size-card',
                size.unlimited || size.quantity > 0 ? 'available' : 'unavailable'
              ]"
              :elevation="size.unlimited || size.quantity > 0 ? 2 : 0"
              rounded="md"
            >
              <v-card-text class="py-2 px-3">
                <div class="d-flex align-center justify-space-between">
                  <div class="d-flex align-center gap-2">
                    <span class="text-subtitle-2 font-weight-bold">
                      {{ size.name }}
                    </span>
                    <v-chip
                      v-if="!size.unlimited"
                      size="x-small"
                      color="warning"
                      variant="flat"
                    >
                      {{ size.quantity }} db
                    </v-chip>
                  </div>

                  <!-- Action Button -->
                  <v-btn
                    v-if="size.unlimited || size.quantity > 0"
                    color="primary"
                    variant="elevated"
                    rounded="lg"
                    class="compact-order-btn"
                    @click="handleOrder(item.id, size.id)"
                  >
                    <v-icon
                      start
                      size="16"
                    >
                      mdi-plus-circle
                    </v-icon>
                    <span>{{ formatPrice(size.price) }}</span>
                  </v-btn>
                  <v-btn
                    v-else
                    color="error"
                    variant="tonal"
                    rounded="lg"
                    class="compact-order-btn"
                    disabled
                  >
                    <v-icon
                      start
                      size="16"
                    >
                      mdi-close-circle
                    </v-icon>
                    <span class="text-medium-emphasis">{{ formatPrice(size.price) }}</span>
                  </v-btn>
                </div>
              </v-card-text>
            </v-card>
          </div>
        </div>
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
import { useFavouritesStore } from "@/stores/favourites";
import { useVendorStore } from "@/stores/vendor";

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
    const favourites = useFavouritesStore();
    const vendorStore = useVendorStore();
    return {
      auth,
      order,
      favourites,
      vendorStore,
    }
  },
  computed: {
    isFavourite() {
      return this.favourites.isMatched(this.item.id);
    },
  },
  methods: {
    handleOrder(itemId, sizeId) {
      this.order.addItem(itemId, sizeId);

      // Optional: Show a brief success feedback
      this.$emit('item-added', { itemId, sizeId });
    },

    async toggleFavourite() {
      const vendorId = this.vendorStore.selectedVendor?.id;
      if (!vendorId) return;
      if (this.isFavourite) {
        const favouriteId = this.favourites.getMatchedFavouriteId(this.item.id);
        await this.favourites.removeFavourite(vendorId, favouriteId);
      } else {
        await this.favourites.addFavourite(vendorId, this.item.name);
        const menuDate = this.order.order?.date_of_order ?? null;
        await this.favourites.fetchMatches(vendorId, menuDate);
        await this.favourites.ensureFavouriteNotificationsEnabled(vendorId);
      }
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

.size-grid {
  display: grid;
  gap: 8px;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

/* Responsive size grid based on layout context */
:global(.layout-1-col) .size-grid {
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

:global(.layout-2-col) .size-grid {
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 8px;
}

:global(.layout-3-col) .size-grid {
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 6px;
}

.size-card {
  transition: all 0.2s ease;
  border: 1px solid rgba(var(--v-theme-outline), 0.2);
  background: rgb(var(--v-theme-surface-container-low));
   padding: 0;
}

.size-card.available {
  border-color: rgba(var(--v-theme-primary), 0.3);
  background: rgb(var(--v-theme-surface-container));
}

.size-card.available:hover {
  transform: translateY(-1px);
  border-color: rgba(var(--v-theme-primary), 0.5);
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
  min-height: 48px;
  box-shadow: 0 2px 8px rgba(var(--v-theme-primary), 0.3);
  transition: all 0.2s ease;
}

.order-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(var(--v-theme-primary), 0.4);
}

.sold-out-btn {
  font-weight: 500;
  text-transform: none;
  min-height: 48px;
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

.v-theme--dark .size-container.available {
  background: rgba(var(--v-theme-primary), 0.1);
}

.v-theme--dark .size-container.unavailable {
  background: rgba(var(--v-theme-surface), 0.5);
}

/* Responsive adjustments */
@media (max-width: 960px) {
  .item-info {
    margin-bottom: 8px;
  }

  .size-grid {
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)) !important;
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

  .size-grid {
    grid-template-columns: 1fr !important;
    gap: 8px;
  }
}

/* Animation for quantity chips */
.v-chip {
  transition: all 0.2s ease;
}

.v-chip:hover {
  transform: scale(1.05);
}

.size-item {
  display: flex;
  flex-direction: column;
}

.compact-order-btn {
  padding: 0 10px;
  height: 32px;
  font-size: 0.75rem;
  text-transform: none;
  min-width: unset;
  white-space: nowrap;
  line-height: 1;
}
</style>
