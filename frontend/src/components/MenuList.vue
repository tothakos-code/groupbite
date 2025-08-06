<template>
  <v-card
    class="menu-card elevation-4 w-100"
    rounded="lg"
  >
    <!-- Header Section -->
    <v-card-title class="header-section pa-4">
      <v-row
        align="center"
        no-gutters
      >
        <v-col
          cols="12"
          sm="6"
          lg="8"
          class="d-none d-sm-flex"
        >
          <div class="header-content">
            <v-icon
              class="me-2"
              size="large"
            >
              mdi-silverware-fork-knife
            </v-icon>
            <div>
              <h2 class="text-h5 font-weight-bold">
                Étlap
              </h2>
              <p class="text-body-2 text-medium-emphasis ma-0">
                {{ selectedDate.toLocaleDateString('hu-HU', {weekday:'long', year: 'numeric', month: 'long', day: 'numeric'}) }}
              </p>
            </div>
          </div>
        </v-col>
        <v-col
          cols="12"
          sm="6"
          lg="4"
        >
          <div class="d-flex justify-center justify-sm-end">
            <Datestamp
              ref="dateSelector"
              :limit-to-current-week="true"
              :set-date="selectedDate.toISODate()"
              @selected-date="(day) => getMenu(day)"
            />
          </div>
        </v-col>
      </v-row>
    </v-card-title>

    <!-- Category Filter Section -->
    <v-card-text
      v-if="menuStore.getItems.length !== 0 && menuStore.getCategories.size > 1"
      class="pa-0"
    >
      <div class="category-filter pa-4">
        <v-chip-group
          v-model="selectedCategoryIndex"
          selected-class="text-white"
          color="primary"
          mandatory
        >
          <v-chip
            v-for="(category, index) in categoryList"
            :key="index"
            :value="index"
            variant="outlined"
            class="ma-1"
            size="default"
          >
            <v-icon
              start
              size="small"
            >
              {{ getCategoryIcon(category) }}
            </v-icon>
            {{ category }}
          </v-chip>
        </v-chip-group>
      </div>
      <v-divider />
    </v-card-text>

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
            >
              <div
                v-for="item in filteredItems"
                :key="`item-${item.id}`"
                class="menu-item-wrapper mb-2"
              >
                <v-hover v-slot="{ isHovering, props }">
                  <MenuItem
                    :item="item"
                    :class="[
                      'menu-item-card',
                      isHovering ? 'item-hover' : ''
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
  </v-card>
</template>

<script>
import Datestamp from "@/components/DateStamp.vue"
import { state, socket } from "@/main";
import { useAuth } from "@/stores/auth";
import { useVendorStore } from "@/stores/vendor";
import { useMenuStore } from "@/stores/menu";
import MenuItem from "../components/MenuItem.vue"

export default {
  name: "MenuList",
  components: {
    Datestamp,
    MenuItem,
  },
  setup() {
    const auth = useAuth();
    const vendorStore = useVendorStore();
    const menuStore = useMenuStore();
    return {
      auth,
      vendorStore,
      menuStore
    }
  },
  data() {
    return {
      selectedCategoryIndex: 0,
      isLoading: true
    }
  },
  computed: {
    selectedDate() {
      return state.selectedDate;
    },
    categoryList() {
      const categories = [...Array.from(this.menuStore.getCategories)];
      return categories;
    },
    selectedCategory() {
      return this.categoryList[this.selectedCategoryIndex] || 'minden';
    },
    filteredItems() {
      const items = this.menuStore.getItems || [];

      // Sort items by category and then by index
      const sortedItems = [...items].sort((a, b) => {
        // First sort by category
        if (a.category !== b.category) {
          return a.category.localeCompare(b.category, 'hu-HU');
        }
        // Then sort by index within the same category
        return (a.index || 0) - (b.index || 0);
      });

      // Filter by selected category
      if (this.selectedCategory === 'minden') {
        return sortedItems;
      }
      return sortedItems.filter(item => item.category === this.selectedCategory);
    }
  },
  watch: {
    'menuStore.getCategories': {
      handler() {
        // Reset to "minden" when categories change
        this.selectedCategoryIndex = 0;
      },
      deep: true
    }
  },
  mounted() {
    this.getMenu()
  },
  methods: {
    getMenu: function(day) {
      this.isLoading = true;

      if (day === undefined) {
        if (state.selectedDate === undefined) {
          day = new Date()
        } else {
          day = state.selectedDate;
        }
      }

      let formated_day = new Date(day).toISODate();

      socket.emit("fe_date_selection", {
        "old_selected_date": state.selectedDate.toISODate(),
        "new_selected_date": formated_day,
        "vendor_id": this.vendorStore.selectedVendor.id,
      });

      state.selectedDate = new Date(day);

      // Set loading to false after a short delay to ensure data is loaded
      setTimeout(() => {
        this.isLoading = false;
      }, 500);

      history.pushState({}, "", `/menu/${this.vendorStore.selectedVendor.name}/${state.selectedDate.toISODate()}`)
    },

    getCategoryIcon(category) {
      const iconMap = {
        'minden': 'mdi-view-grid',
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
    },

    getCurrentWeekDates() {
      const currentDate = new Date();
      const currentDayOfWeek = currentDate.getAdjustedDay();

      // Calculate the start date of the current week (Monday)
      const startDate = new Date(currentDate);
      startDate.setDate(currentDate.getDate() - currentDayOfWeek);

      const weekDates = [];

      // Loop through the days of the week and format the dates
      for (let i = 0; i < 7; i++) {
        const currentDate = new Date(startDate);
        currentDate.setDate(startDate.getDate() + i);

        const formattedDate = currentDate.toISODate();
        weekDates.push(formattedDate);
      }

      return weekDates;
    },
  }
}
</script>

<style scoped>
.menu-card {
  background: rgb(var(--v-theme-surface));
  border: 1px solid rgb(var(--v-theme-outline));
  width: 100%;
  max-width: 100%;
}

.header-section {
  background: rgb(var(--v-theme-primary));
  color: rgb(var(--v-theme-on-primary));
}

.header-content {
  display: flex;
  align-items: center;
}

.category-filter {
  background: rgb(var(--v-theme-surface));
  backdrop-filter: blur(10px);
}

.menu-item-wrapper {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.menu-item-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 12px !important;
  background: rgb(var(--v-theme-surface));
  border: 1px solid rgb(var(--v-theme-outline));
}

.item-hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(var(--v-theme-shadow), 0.15) !important;
  border-color: rgba(var(--v-theme-primary), 0.3) !important;
}

.v-chip {
  font-weight: 500;
  text-transform: capitalize;
}

.v-chip--selected {
  transform: scale(1.05);
}

/* Custom scrollbar that adapts to theme */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: rgb(var(--v-theme-surface-variant));
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: rgb(var(--v-theme-outline));
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgb(var(--v-theme-on-surface-variant));
}

/* Dark theme specific adjustments */
.v-theme--dark .menu-card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.v-theme--dark .item-hover {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4) !important;
}

@media (max-width: 600px) {
  .header-section {
    text-align: center;
  }

  .category-filter {
    padding: 16px 8px !important;
  }
}
</style>
