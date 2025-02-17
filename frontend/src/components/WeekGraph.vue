<template>
  <v-card class="border-sm">
    <v-card-title class="bg-header d-flex border-b-sm justify-content-center">
      <v-row
        cols="12"
        class=""
      >
        <v-col
          cols="auto"
          class="col-12 d-flex justify-content-center col-sm-6 col-md-4 justify-content-md-start"
        >
          <h2 class="">
            Rendelés statisztikák
          </h2>
        </v-col>
      </v-row>
    </v-card-title>
    <v-card-text class="">
      <v-row class="">
        <v-col
          cols="12"
          lg="6"
          class="px-lg-5"
        >
          <v-row class="justify-content-center">
            <p>
              Utolsó év rendeléseinek összesítése havi bontásban
            </p>
          </v-row>
          <Bar
            v-if="vendorChartLoaded"
            id="my-chart-id"
            class="col-6"
            :options="chartOptions"
            :data="yearChartData"
          />
        </v-col>
        <v-col
          cols="12"
          lg="6"
          class="px-lg-5"
        >
          <v-row class="justify-content-center">
            <p>
              Utolsó hét rendelésinek összesítése napi bontásban
            </p>
          </v-row>
          <Bar
            v-if="weekChartLoaded"
            id="my-chart-id"
            class="col-6"
            :options="chartOptions"
            :data="weekChartData"
          />
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
import { useAuth } from "@/stores/auth";
import { useOrderStore } from "@/stores/order";
import { useVendorStore } from "@/stores/vendor";
import { ref } from "vue";
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

export default {
  name: "WeekSummary",
  components: {
    Bar
  },
  emits: ["close"],
  setup() {
    const user_states = ref({});
    const weekdates = ref([]);
    const auth = useAuth();
    const orderStore = useOrderStore();
    const vendorStore = useVendorStore();
    return {
      auth,
      orderStore,
      vendorStore,
      user_states,
      weekdates
    }
  },
  data() {
    return {
      currentDateSelected: new Date(),
      weekChartData: {
        labels: [ 'Hétfő', 'Kedd', 'Szerda', 'Csütörtök', 'Péntek', 'Szombat', 'Vasárnap' ],
        datasets: []
      },
      yearChartData: {
        labels: [ 'Jan', 'Feb', 'Már', 'Ápr', 'Máj', 'Jun', 'Jul', 'Aug', 'Sze', 'Okt', 'Nov', 'Dec' ],
        datasets: []
      },
      vendorChartLoaded: false,
      weekChartLoaded: false,
      chartOptions: {
        responsive: true
      }
    }
  },
  computed: {
    getCurrentMonthName() {
      return this.currentDateSelected.toLocaleDateString("hu-HU", {month:"long"});
    },
    getTodayDayName() {
      return this.currentDateSelected.toLocaleDateString("hu-HU", {weekday:"long"});
    },
    getTodayDayDate() {
      return this.currentDateSelected.toLocaleDateString("hu-HU");
    },
    orderCount(){
      let sum = 0;
      for (const date in this.history) {
        sum += Object.keys(this.history[date]).length;
      }
      return sum;
    }
  },
  mounted() {
    this.getStats()
  },
  methods: {
    backgroundColor: function(str) {

      var hash = 0;
      let s = 30;
      let l = 70;
      for (var i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
      }
      var h = hash % 360;
      s /= 100;
      l /= 100;

      let c = (1 - Math.abs(2 * l - 1)) * s,
          x = c * (1 - Math.abs((h / 60) % 2 - 1)),
          m = l - c/2,
          r = 0,
          g = 0,
          b = 0;

      if (0 <= h && h < 60) {
        r = c; g = x; b = 0;
      } else if (60 <= h && h < 120) {
        r = x; g = c; b = 0;
      } else if (120 <= h && h < 180) {
        r = 0; g = c; b = x;
      } else if (180 <= h && h < 240) {
        r = 0; g = x; b = c;
      } else if (240 <= h && h < 300) {
        r = x; g = 0; b = c;
      } else if (300 <= h && h < 360) {
        r = c; g = 0; b = x;
      }
      // Having obtained RGB, convert channels to hex
      r = Math.round((r + m) * 255).toString(16);
      g = Math.round((g + m) * 255).toString(16);
      b = Math.round((b + m) * 255).toString(16);

      // Prepend 0s, if necessary
      if (r.length == 1)
        r = "0" + r;
      if (g.length == 1)
        g = "0" + g;
      if (b.length == 1)
        b = "0" + b;

      return "#" + r + g + b;

    },
    getStats: function(){
      this.orderStore.stats()
        .then(response => {
            if (response.status === 200) {
              this.yearChartData.labels = response.data.data.year_data.labels
              for (const [key, value] of Object.entries(response.data.data.year_data.data)) {
                this.yearChartData.datasets.push({
                  label: key,
                  backgroundColor: this.backgroundColor(key),
                  data: value.data
                })
              }
              this.vendorChartLoaded = true
              this.weekChartData.labels = response.data.data.week_data.labels
              for (const [key, value] of Object.entries(response.data.data.week_data.data)) {
                this.weekChartData.datasets.push({
                  label: key,
                  backgroundColor: this.backgroundColor(key),
                  data: value.data
                })
              }
              this.weekChartLoaded = true
            }
        })
    },
    async getCurrentWeekDates(date) {
      const weekDates = [];
      const weekStart = new Date(date);
      weekStart.setDate(weekStart.getDate() - weekStart.getAdjustedDay())
      weekStart.setHours(12, 0, 0, 0);
      for (let i = 0; i <= 6; i++) {
        const iterDate = new Date(weekStart);
        iterDate.setDate(weekStart.getDate()+ i)
        const formattedDate = iterDate.toISODate();
        weekDates.push(formattedDate);
      }
      return weekDates;
    },
    setDay: function(day) {
      const newDate = new Date(day);

      this.weekdates.value = this.getCurrentWeekDates(newDate).then(res => {
        this.weekdates = res;
      });

      this.currentDateSelected = newDate;
    },
    nextWeek: function() {
      let nextWeek = this.currentDateSelected
      nextWeek.setDate(nextWeek.getDate() + 7)
      this.setDay(nextWeek)
    },
    prevWeek: function() {
      let nextWeek = this.currentDateSelected
      nextWeek.setDate(nextWeek.getDate() - 7)
      this.setDay(nextWeek)
    },
  }
}
</script>

<style>

</style>
