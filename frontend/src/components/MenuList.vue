<template>
  <div class="card">
    <div class="card-header row col px-2">
      <div class="col-0 d-none d-sm-inline col-sm-6 col-lg-8 my-auto">
        <h2 class="text-nowrap">
          Étlap - {{ selectedDate.toLocaleDateString('hu-HU', {weekday:'long'}) }}
        </h2>
      </div>
      <div class="col-12 d-flex justify-content-center col-sm-6 col-lg-4 px-0">
        <Datestamp
          ref="dateSelector"
          :limit-to-current-week="true"
          :set-date="selectedDate.toISODate()"
          @selected-date="(day) => getMenu(day)"
        />
      </div>
    </div>
    <div class="row">
      <div
        v-for="category, index in categories"
        :key="index"
        class="d-flex justify-content-center flex-fill col-6 col-sm-4 col-lg-3 col-xxl-1"
      >
        <input
          :id="category"
          type="radio"
          name="daySelectionRadio"
          class="btn-check"
          role="button"
        >
        <label
          :for="category"
          class="btn btn-sm my-1 rounded rounded-5 text-nowrap d-flex align-items-center"
          :class="['btn-outline-' + auth.getUserColor]"
          @click="setFilter(category)"
        >
          {{ category }}
        </label>
      </div>
    </div>
    <div class="row col list-group border-0">
      <div class="col">
        <div class="list-group m-1">
          <MenuItem
            v-for="(item, i) in itemlist"
            :key="'item-'+i"
            :item="item"
          />
          <div
            v-if="itemlist.length === 0"
            class="d-flex justify-content-center"
          >
            <span>Erre a napra nincsen mit betöltenem</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Datestamp from "@/components/DateStamp.vue"
import { state, socket } from "@/main";
import { useAuth } from "@/stores/auth";
import { useVendorStore } from "@/stores/vendor";
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
    return {
      auth,
      vendorStore
    }
  },
  data() {
    return {
      itemlist: [],
      filter:[],
      categories: new Set(["minden"])
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
    loadMenu(day) {
      if (day === undefined) {
        day = new Date().toISODate()
      }
      this.vendorStore.fetchMenusByDate(this.vendorStore.selectedVendor.id, day, {
          "filter": this.filter
        })
        .then(response => {
          this.itemlist = response.data.data;
          // this.categories = new Set(["minden"])
          for (var item of this.itemlist) {
            this.categories.add(item.category)
          }
        })
        .catch(error => console.error(error));
    },
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
        "vendor_id": this.vendorStore.selectedVendor.id
      })
      state.selectedDate = new Date(day);
      history.pushState({}, "", `/menu/${this.vendorStore.selectedVendor.name}/${state.selectedDate.toISODate()}`)
      this.loadMenu(formated_day);
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
    setFilter(category) {
      if (category === "minden") {
        this.filter = [];
      } else {
        this.filter = [category];
      }
      this.loadMenu(state.selectedDate.toISODate());
    }
  }
}
</script>

<style>
[data-bs-theme=light] .list-group-item:hover {
  background-color: lightgray;
}
[data-bs-theme=dark] .list-group-item:hover {
  background-color: #3c3c3c;
}
</style>
