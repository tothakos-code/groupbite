<template>
  <div>
    <!-- Layout Control Header -->
    <div class="layout-controls d-flex align-center justify-space-between pa-3 mb-2">
      <div class="d-flex align-center">
        <v-icon
          size="20"
          class="me-2 text-medium-emphasis"
        >
          mdi-view-grid
        </v-icon>
        <span class="text-body-2 text-medium-emphasis">
          Nézet
        </span>
      </div>

      <v-btn-toggle
        v-model="selectedLayout"
        mandatory
        density="compact"
        variant="outlined"
        divided
        @update:model-value="$emit('layout-changed', selectedLayout)"
      >
        <v-btn
          value="1"
          size="small"
          :active="selectedLayout === '1'"
        >
          <v-icon size="16">
            mdi-view-list
          </v-icon>
          <v-tooltip
            activator="parent"
            location="bottom"
          >
            1 oszlop
          </v-tooltip>
        </v-btn>

        <v-btn
          value="2"
          size="small"
          :active="selectedLayout === '2'"
        >
          <v-icon size="16">
            mdi-view-grid
          </v-icon>
          <v-tooltip
            activator="parent"
            location="bottom"
          >
            2 oszlop
          </v-tooltip>
        </v-btn>

        <v-btn
          value="3"
          size="small"
          :active="selectedLayout === '3'"
        >
          <v-icon size="16">
            mdi-view-grid-plus
          </v-icon>
          <v-tooltip
            activator="parent"
            location="bottom"
          >
            3 oszlop
          </v-tooltip>
        </v-btn>
      </v-btn-toggle>
    </div>

    <!-- Menu Items Section -->
    <v-card-text class="pa-0">
      <v-container
        v-if="filteredItems.length > 0"
        fluid
        class="pa-0"
      >
        <v-row class="ma-0">
          <v-col
            cols="12"
            class="pa-2"
          >
            <v-fade-transition
              group
              tag="div"
              :class="gridClass"
            >
              <div
                v-for="item in filteredItems"
                :key="`item-${item.id}`"
                class="menu-item-wrapper"
              >
                <v-hover v-slot="{ isHovering, props }">
                  <MenuItem
                    :item="item"
                    :class="[
                      'menu-item-card',
                      isHovering ? 'item-hover' : '',
                      `layout-${selectedLayout}-col`
                    ]"
                    v-bind="props"
                  />
                </v-hover>
              </div>
            </v-fade-transition>
          </v-col>
        </v-row>
      </v-container>

      <!-- Empty State -->
      <v-container
        v-else-if="!isLoading"
        fluid
        class="pa-0"
      >
        <div class="text-center py-8 px-4">
          <v-icon
            size="64"
            color="grey-lighten-1"
            class="mb-4"
          >
            mdi-food-off
          </v-icon>
          <h3 class="text-h6 text-medium-emphasis mb-2">
            Nincs elérhető menü
          </h3>
          <p class="text-body-2 text-medium-emphasis">
            Erre a napra jelenleg nincsen menü betöltve.
          </p>
        </div>
      </v-container>

      <!-- Loading State -->
      <v-container
        v-if="isLoading"
        fluid
        class="pa-0"
      >
        <div class="text-center py-8 px-4">
          <v-progress-circular
            indeterminate
            size="64"
            color="primary"
            class="mb-4"
          />
          <p class="text-body-1 text-medium-emphasis">
            Menü betöltése...
          </p>
        </div>
      </v-container>
    </v-card-text>
  </div>
</template>

<script>
import MenuItem from "../components/MenuItem.vue"

export default {
  name: 'MenuLayoutChanger',
  components: {
    MenuItem,
  },
  props: {
    filteredItems: {
      type: Array,
      required: true,
    },
    isLoading: {
      type: Boolean,
      default: false
    },
    initialLayout: {
      type: String,
      default: '2',
      validator: (value) => ['1', '2', '3'].includes(value)
    }
  },
  emits: ['layout-changed'],
  data() {
    return {
      selectedLayout: this.initialLayout
    }
  },
  computed: {
    gridClass() {
      const baseClass = 'menu-grid transition-all';
      switch (this.selectedLayout) {
        case '1':
          return `${baseClass} one-column-grid`;
        case '2':
          return `${baseClass} two-column-grid`;
        case '3':
          return `${baseClass} three-column-grid`;
        default:
          return `${baseClass} two-column-grid`;
      }
    }
  },
  watch: {
    initialLayout: {
      immediate: true,
      handler(newVal) {
        this.selectedLayout = newVal;
      }
    }
  }
}
</script>

<style scoped>
.layout-controls {
  background: rgb(var(--v-theme-surface-container-low));
  border: 1px solid rgb(var(--v-theme-outline));
  border-radius: 8px;
  backdrop-filter: blur(10px);
}

.menu-grid {
  display: grid;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.one-column-grid {
  grid-template-columns: 1fr;
  gap: 16px;
}

.two-column-grid {
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.three-column-grid {
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
}

.menu-item-wrapper {
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Layout-specific card adjustments */
.layout-1-col {
  /* Larger cards for single column */
  min-height: auto;
}

.layout-2-col {
  /* Medium sized cards */
  min-height: auto;
}

.layout-3-col {
  /* Smaller, more compact cards */
  min-height: auto;
}

.layout-3-col .size-container {
  min-height: 50px !important;
}

.layout-3-col .text-h6 {
  font-size: 1rem !important;
}

.layout-3-col .text-body-2 {
  font-size: 0.75rem !important;
}

/* Hover effects */
.item-hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(var(--v-theme-shadow), 0.15) !important;
  border-color: rgba(var(--v-theme-primary), 0.3) !important;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .three-column-grid {
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }
}

@media (max-width: 768px) {
  .two-column-grid,
  .three-column-grid {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .layout-controls {
    padding: 12px 16px !important;
  }
}

@media (max-width: 480px) {
  .one-column-grid,
  .two-column-grid,
  .three-column-grid {
    gap: 6px;
  }

  .layout-controls {
    flex-direction: column;
    gap: 8px;
    text-align: center;
  }
}

/* Dark theme adjustments */
.v-theme--dark .layout-controls {
  background: rgba(var(--v-theme-surface-container), 0.8);
  border-color: rgba(var(--v-theme-outline), 0.4);
}

.v-theme--dark .item-hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4) !important;
}

/* Button toggle styling */
.v-btn-toggle {
  border: 1px solid rgba(var(--v-theme-outline), 0.4);
  border-radius: 6px;
  overflow: hidden;
}

.v-btn-toggle .v-btn {
  border: none !important;
  min-width: 40px;
}

.v-btn-toggle .v-btn:not(:last-child) {
  border-right: 1px solid rgba(var(--v-theme-outline), 0.4) !important;
}

/* Animation classes */
.transition-all {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Stagger animation for grid items */
.menu-item-wrapper {
  animation: fadeInUp 0.4s ease forwards;
  opacity: 0;
  transform: translateY(20px);
}

.menu-item-wrapper:nth-child(1) { animation-delay: 0ms; }
.menu-item-wrapper:nth-child(2) { animation-delay: 50ms; }
.menu-item-wrapper:nth-child(3) { animation-delay: 100ms; }
.menu-item-wrapper:nth-child(4) { animation-delay: 150ms; }
.menu-item-wrapper:nth-child(5) { animation-delay: 200ms; }
.menu-item-wrapper:nth-child(6) { animation-delay: 250ms; }

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
