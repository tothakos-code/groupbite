<template>
  <v-card class="border-sm w-100">
    <v-card-title class="bg-header border-b-sm  px-2">
      <v-row justify="space-between">
        <v-col class="col-0 d-none d-sm-inline col-sm-6 col-lg-8 my-auto">
          <h2 class="text-nowrap">
            Étlap - {{ selectedDate.toLocaleDateString('hu-HU', {weekday:'long'}) }}
          </h2>
        </v-col>
        <v-col class="col-12 d-flex justify-content-center col-sm-6 col-lg-4 px-0">
          <Datestamp
            ref="dateSelector"
            :limit-to-current-week="true"
            :set-date="selectedDate.toISODate()"
            @selected-date="(day) => getMenu(day)"
          />
        </v-col>
      </v-row>
    </v-card-title>
    <v-chip-group
      v-if="menuStore.getItems.length !== 0 && menuStore.getCategories.size > 1"
    >
      <v-row
        class="mx-0 mb-0 border-b-md"
      >
        <v-col class="d-flex justify-space-around">
          <v-chip
            v-for="category, index in menuStore.getCategories"
            :key="index"
            variant="outlined"
            selected-class="bg-secondary"
            class="text-primary"
            @click="filter=category"
          >
            {{ category }}
          </v-chip>
        </v-col>
      </v-row>
    </v-chip-group>
    <v-card-text class="p-0">
      <v-row>
        <v-col>
          <v-list>
            <div
              v-for="(item, i) in menuStore.getItems"
              :key="'item-'+i"
            >
              <template
                v-if="filter==='minden' || item.category === filter"
              >
                <v-hover v-slot="{ isHovering, props }">
                  <MenuItem
                    :key="'item-'+i"
                    :item="item"
                    :class="isHovering ? 'bg-secondary' : undefined"
                    v-bind="props"
                  />
                </v-hover>
              </template>
            </div>
            <div
              v-if="menuStore.getItems.length === 0 && isLoading === false"
              class="d-flex justify-content-center"
            >
              <span>Erre a napra nincsen mit betöltenem</span>
            </div>
            <div
              v-if="isLoading === true"
              class="d-flex justify-content-center"
            >
              <div
                class="spinner-border"
                role="status"
              >
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
          </v-list>
        </v-col>
      </v-row>
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
      filter: "minden",
      isLoading: true
    }
  },
  computed: {
    selectedDate() {
      return state.selectedDate;
    }
  },
  mounted() {
    this.getMenu()
  },
  methods: {
    getMenu: function(day) {
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
      })
      state.selectedDate = new Date(day);
      this.isLoading = false
      history.pushState({}, "", `/menu/${this.vendorStore.selectedVendor.name}/${state.selectedDate.toISODate()}`)
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

<style>

</style>
