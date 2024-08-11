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
    <div class="row col list-group">
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
import axios from "axios";
import MenuItem from "../components/MenuItem.vue"


export default {
  name: "MenuList",
  components: {
    Datestamp,
    MenuItem,
  },
  setup() {
    const auth = useAuth();
    return {
      auth
    }
  },
  data() {
    return {
      itemlist: [],
      others: {"0":"[]","1":"[]","2":"[]","3":"[]","4":"[]","5":"[]","6":"[]"},
      dayTitles: {
        "0":"Hétfői menü",
        "1":"Keddi menü",
        "2":"Szerdai menü",
        "3":"Csütörtöki menü",
        "4":"Pénteki menü",
        "5":"Szombati menü",
        "6":"Vasárnapi menü"
      }
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
      let url = `http://${window.location.host}/api/menu/get/${state.selected_vendor.id}/${day}`;

      axios.get(url)
        .then(response => {
          this.itemlist = response.data;
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
        "vendor_id": state.selected_vendor.id
      })
      state.selectedDate = new Date(day);
      history.pushState({}, "", `/menu/${state.selected_vendor.name}/${state.selectedDate.toISODate()}`)
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
