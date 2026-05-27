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
    <template v-if="selectedCategory === 'minden'">
      <!-- Single shared layout toggle for all category groups -->
      <div class="layout-controls d-flex align-center justify-space-between pa-3 mb-2 mx-3 mt-3">
        <div class="d-flex align-center">
          <v-icon
            size="20"
            class="me-2 text-medium-emphasis"
          >
            mdi-view-grid
          </v-icon>
          <span class="text-body-2 text-medium-emphasis">Nézet</span>
        </div>
        <v-btn-toggle
          v-model="currentLayout"
          mandatory
          density="compact"
          variant="outlined"
          divided
          @update:model-value="handleLayoutChange"
        >
          <v-btn
            value="1"
            size="small"
          >
            <v-icon size="16">mdi-view-list</v-icon>
          </v-btn>
          <v-btn
            value="2"
            size="small"
          >
            <v-icon size="16">mdi-view-grid</v-icon>
          </v-btn>
          <v-btn
            value="3"
            size="small"
          >
            <v-icon size="16">mdi-view-grid-plus</v-icon>
          </v-btn>
        </v-btn-toggle>
      </div>

      <template
        v-for="group in groupedItems"
        :key="group.category"
      >
        <div class="d-flex align-center my-3 px-4">
          <v-divider color="primary" />
          <span class="mx-3 text-primary text-subtitle-2 font-weight-bold text-uppercase text-no-wrap">
            {{ group.category }}
          </span>
          <v-divider color="primary" />
        </div>
        <MenuLayoutChanger
          :filtered-items="group.items"
          :is-loading="isLoading"
          :initial-layout="currentLayout"
          :show-controls="false"
          @layout-changed="handleLayoutChange"
        />
      </template>
    </template>
    <MenuLayoutChanger
      v-else
      :filtered-items="filteredItems"
      :is-loading="isLoading"
      :initial-layout="currentLayout"
      @layout-changed="handleLayoutChange"
    />
  </v-card>
</template>

<script>
import Datestamp from "@/components/DateStamp.vue"
import { state, socket } from "@/main";
import { useAuth } from "@/stores/auth";
import { useVendorStore } from "@/stores/vendor";
import { useMenuStore } from "@/stores/menu";
// import MenuItem from "../components/MenuItem.vue"
import MenuLayoutChanger from "../components/LayoutChanger.vue"

export default {
  name: "MenuList",
  components: {
    Datestamp,
    MenuLayoutChanger,
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
      isLoading: true,
      currentLayout: localStorage.getItem('menuLayout') || '2'
    }
  },
  watch: {
    selectedCategoryIndex(newIdx) {
      const category = this.categoryList[newIdx];
      const url = new URL(window.location.href);
      if (category && category !== 'minden') {
        url.searchParams.set('category', category);
      } else {
        url.searchParams.delete('category');
      }
      history.replaceState({}, '', url.toString());
    },
    categoryList(newList) {
      if (!newList.length) return;
      const cat = new URLSearchParams(window.location.search).get('category');
      if (!cat) return;
      const idx = newList.indexOf(cat);
      if (idx !== -1) {
        this.selectedCategoryIndex = idx;
      }
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
      const sortedItems = [...items].sort((a, b) => {
        const catA = a.category || '';
        const catB = b.category || '';
        if (catA !== catB) return catA.localeCompare(catB, 'hu-HU');
        return (a.index || 0) - (b.index || 0);
      });
      if (this.selectedCategory === 'minden') {
        return sortedItems;
      }
      return sortedItems.filter(item => item.category === this.selectedCategory);
    },
    groupedItems() {
      const items = this.menuStore.getItems || [];
      const sorted = [...items].sort((a, b) => {
        const catA = a.category || '';
        const catB = b.category || '';
        if (catA !== catB) return catA.localeCompare(catB, 'hu-HU');
        return (a.index || 0) - (b.index || 0);
      });
      const map = new Map();
      for (const item of sorted) {
        const cat = item.category || null;
        if (!map.has(cat)) map.set(cat, []);
        map.get(cat).push(item);
      }
      const result = [];
      for (const [cat, groupItems] of map) {
        if (cat !== null) result.push({ category: cat, items: groupItems });
      }
      if (map.has(null)) {
        result.push({ category: this.$t('menu.category.other'), items: map.get(null) });
      }
      return result;
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
      }, () => {
          this.isLoading = false;
      });
      state.selectedDate = new Date(day);
      history.pushState({}, '', `/menu/${this.vendorStore.selectedVendor.name}/${state.selectedDate.toISODate()}${window.location.search}`)
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
    handleLayoutChange(layout) {
      this.currentLayout = layout;
      localStorage.setItem('menuLayout', layout);
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

.layout-controls {
  background: rgb(var(--v-theme-surface-container-low));
  border: 1px solid rgb(var(--v-theme-outline));
  border-radius: 8px;
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

.two-column-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.menu-item-wrapper {
  display: flex;
  flex-direction: column;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .two-column-grid {
    grid-template-columns: 1fr;
    gap: 8px;
  }
}

@media (max-width: 480px) {
  .two-column-grid {
    gap: 6px;
  }
}

/* Optional: Masonry-like effect for varied heights */
.two-column-grid.masonry {
  grid-auto-rows: min-content;
}

/* Hover effects */
.item-hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(var(--v-theme-shadow), 0.15) !important;
}

/* Dark theme adjustments */
.v-theme--dark .item-hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4) !important;
}
</style>
