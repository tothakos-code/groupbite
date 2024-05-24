<template>
  <div class="card">
    <div class="card-header row d-flex px-2">
      <div class="col-3 col-md-6 col-lg-8 row px-0">
        <div class="col-0 d-none d-sm-inline col-sm-6 col-lg-4 my-auto">
          <h2 class="text-nowrap">
            Étlap
          </h2>
        </div>
        <div class="col-0 d-none col-lg-8 d-lg-inline my-auto truncate">
          <!-- <TransferPopup /> -->
        </div>
      </div>
      <div class="col-12 col-sm-6 col-md-6 col-lg-4 d-flex flex-fill ">
        <Datestamp
          ref="dateSelector"
          :limit-to-current-week="true"
          :set-date="selectedDate.toISODate()"
          @selected-date="(day) => getMenu(day)"
        />
      </div>
    </div>
    <!-- <div class="row d-flex justify-content-evenly">
      <div
        v-for="date,index in getCurrentWeekDates()"
        :key="index"
        class="d-flex justify-content-center flex-fill col-6 col-sm-4 col-lg-3 col-xxl-1"
      >
        <input
          :id="date"
          type="radio"
          name="daySelectionRadio"
          class="btn-check"
          role="button"
          :checked="date == new Date(selectedDate).toISODate()"
          @click="loadMenu(date)"
        >
        <label
          :for="date"
          class="btn btn-sm my-1 rounded rounded-5 text-nowrap d-flex align-items-center"
          :class="['btn-outline-' + auth.userColor.value]"
        >
          {{ dayTitles[index] }}
        </label>
      </div>
    </div> -->
    <div class="row col list-group">
      <div class="col">
        <div class="list-group m-1">
          <MenuItem
            v-for="(item, index) in menulist"
            :key="index"
            :item="item"
          />
          <div
            v-if="menulist.length === 0"
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
import Datestamp from '@/components/DateStamp.vue'
import { state, socket } from "@/socket";
import { useAuth } from "@/auth";
import axios from 'axios';
import MenuItem from '../components/MenuItem.vue'


export default {
  name: 'MenuList',
  components: {
    Datestamp,
    MenuItem
  },
  setup() {
    const auth = useAuth();
    return {
      auth
    }
  },
  data() {
    return {
      menulist: [],
      others: {'0':'[]','1':'[]','2':'[]','3':'[]','4':'[]','5':'[]','6':'[]'},
      dayTitles: {
        '0':'Hétfői menü',
        '1':'Keddi menü',
        '2':'Szerdai menü',
        '3':'Csütörtöki menü',
        '4':'Pénteki menü',
        '5':'Szombati menü',
        '6':'Vasárnapi menü'
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
          this.menulist = response.data;
        })
        .catch(error => console.error(error));
    },
    getMenu: function(day) {
      if (day === undefined) {
        day = new Date()
        if (day.getHours() >= 13) {
          day.setDate(day.getDate() +1)
        }
      }
      let formated_day = new Date(day).toISODate();
      socket.emit("fe_date_selection", {
        "old_selected_date": state.selectedDate.toISODate(),
        "new_selected_date": formated_day,
        "vendor_id": state.selected_vendor.id
      })
      state.selectedDate = new Date(day);
      if (state.selectedDate.toISODate() === new Date().toISODate()) {
        history.pushState({}, "", `/menu/${state.selected_vendor.name}`)
      } else {
        history.pushState({}, "", `/menu/${state.selected_vendor.name}/${state.selectedDate.toISODate()}`)
      }
      this.loadMenu(formated_day);
    },
    getCurrentWeekDates() {
      const currentDate = new Date();
      const currentDayOfWeek = currentDate.getDay();

      // Calculate the start date of the current week (Sunday)
      const startDate = new Date(currentDate);
      startDate.setDate(currentDate.getDate() - currentDayOfWeek + (currentDayOfWeek === 0 ? -6 : 1));

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
