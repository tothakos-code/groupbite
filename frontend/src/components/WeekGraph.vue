<template>
  <v-container
    fluid
    class="pa-4"
  >
    <v-card
      elevation="2"
      class="mx-auto"
    >
      <!-- Header -->
      <v-card-title class="bg-primary text-white pa-4">
        <v-row
          align="center"
          no-gutters
        >
          <v-col>
            <h2 class="text-h5 font-weight-bold">
              <v-icon class="me-2">
                mdi-chart-bar
              </v-icon>
              Rendelés statisztikák
            </h2>
          </v-col>
        </v-row>
      </v-card-title>

      <!-- Charts Content -->
      <v-card-text class="pa-6">
        <v-row>
          <!-- Year Chart -->
          <v-col
            cols="12"
            lg="6"
          >
            <v-card
              variant="outlined"
              class="chart-card h-100"
              elevation="1"
            >
              <v-card-title class="text-center pa-4 bg-grey-lighten-5">
                <div class="d-flex align-center justify-center">
                  <v-icon
                    class="me-2"
                    color="primary"
                  >
                    mdi-calendar-month
                  </v-icon>
                  <span class="text-h6 font-weight-medium">
                    Éves összesítés
                  </span>
                </div>
              </v-card-title>

              <v-card-subtitle class="text-center pb-0">
                <p class="text-body-2 text-grey-darken-1 ma-0">
                  Utolsó év rendeléseinek összesítése havi bontásban
                </p>
              </v-card-subtitle>

              <v-card-text class="pa-4">
                <!-- Loading State for Year Chart -->
                <div
                  v-if="!vendorChartLoaded"
                  class="text-center py-8"
                >
                  <v-progress-circular
                    indeterminate
                    color="primary"
                    size="64"
                  />
                  <div class="text-body-2 text-grey-darken-1 mt-4">
                    Statisztikák betöltése...
                  </div>
                </div>

                <!-- Year Chart -->
                <div
                  v-else
                  class="chart-container"
                >
                  <Bar
                    id="year-chart"
                    :options="yearChartOptions"
                    :data="yearChartData"
                  />
                </div>
              </v-card-text>
            </v-card>
          </v-col>

          <!-- Week Chart -->
          <v-col
            cols="12"
            lg="6"
          >
            <v-card
              variant="outlined"
              class="chart-card h-100"
              elevation="1"
            >
              <v-card-title class="text-center pa-4 bg-grey-lighten-5">
                <div class="d-flex align-center justify-center">
                  <v-icon
                    class="me-2"
                    color="primary"
                  >
                    mdi-calendar-week
                  </v-icon>
                  <span class="text-h6 font-weight-medium">
                    Heti összesítés
                  </span>
                </div>
              </v-card-title>

              <v-card-subtitle class="text-center pb-0">
                <p class="text-body-2 text-grey-darken-1 ma-0">
                  Utolsó hét rendeléseinek összesítése napi bontásban
                </p>
              </v-card-subtitle>

              <v-card-text class="pa-4">
                <!-- Loading State for Week Chart -->
                <div
                  v-if="!weekChartLoaded"
                  class="text-center py-8"
                >
                  <v-progress-circular
                    indeterminate
                    color="primary"
                    size="64"
                  />
                  <div class="text-body-2 text-grey-darken-1 mt-4">
                    Statisztikák betöltése...
                  </div>
                </div>

                <!-- Week Chart -->
                <div
                  v-else
                  class="chart-container"
                >
                  <Bar
                    id="week-chart"
                    :options="weekChartOptions"
                    :data="weekChartData"
                  />
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Summary Statistics -->
        <v-row
          v-if="vendorChartLoaded && weekChartLoaded"
          class="mt-6"
        >
          <v-col cols="12">
            <v-divider class="mb-4" />
            <h3 class="text-h6 font-weight-medium mb-4 text-center">
              <v-icon class="me-2">
                mdi-information
              </v-icon>
              Összesítő információk
            </h3>
          </v-col>

          <v-col
            cols="12"
            sm="6"
            md="3"
          >
            <v-card
              variant="tonal"
              color="primary"
              class="text-center pa-4"
            >
              <v-card-text class="pa-2">
                <v-icon
                  size="32"
                  class="mb-2"
                >
                  mdi-store
                </v-icon>
                <div class="text-h6 font-weight-bold">
                  {{ getTotalVendors() }}
                </div>
                <div class="text-body-2">
                  Aktív üzletek
                </div>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col
            cols="12"
            sm="6"
            md="3"
          >
            <v-card
              variant="tonal"
              color="success"
              class="text-center pa-4"
            >
              <v-card-text class="pa-2">
                <v-icon
                  size="32"
                  class="mb-2"
                >
                  mdi-calendar-month
                </v-icon>
                <div class="text-h6 font-weight-bold">
                  {{ getTotalYearOrders() }}
                </div>
                <div class="text-body-2">
                  Éves rendelések
                </div>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col
            cols="12"
            sm="6"
            md="3"
          >
            <v-card
              variant="tonal"
              color="info"
              class="text-center pa-4"
            >
              <v-card-text class="pa-2">
                <v-icon
                  size="32"
                  class="mb-2"
                >
                  mdi-calendar-week
                </v-icon>
                <div class="text-h6 font-weight-bold">
                  {{ getTotalWeekOrders() }}
                </div>
                <div class="text-body-2">
                  Heti rendelések
                </div>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col
            cols="12"
            sm="6"
            md="3"
          >
            <v-card
              variant="tonal"
              color="warning"
              class="text-center pa-4"
            >
              <v-card-text class="pa-2">
                <v-icon
                  size="32"
                  class="mb-2"
                >
                  mdi-trending-up
                </v-icon>
                <div class="text-h6 font-weight-bold">
                  {{ getAverageOrdersPerMonth().toFixed(1) }}
                </div>
                <div class="text-body-2">
                  Átlag/hónap
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-container>
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
  name: "OrderStatistics",
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
        labels: ['Hétfő', 'Kedd', 'Szerda', 'Csütörtök', 'Péntek', 'Szombat', 'Vasárnap'],
        datasets: []
      },
      yearChartData: {
        labels: ['Jan', 'Feb', 'Már', 'Ápr', 'Máj', 'Jun', 'Jul', 'Aug', 'Sze', 'Okt', 'Nov', 'Dec'],
        datasets: []
      },
      vendorChartLoaded: false,
      weekChartLoaded: false,
      baseChartOptions: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              usePointStyle: true,
              padding: 20,
              font: {
                size: 12
              }
            }
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: 'white',
            bodyColor: 'white',
            borderColor: 'rgba(255, 255, 255, 0.1)',
            borderWidth: 1,
            cornerRadius: 8,
            displayColors: true
          }
        },
        scales: {
          x: {
            grid: {
              display: false
            },
            ticks: {
              font: {
                size: 11
              }
            }
          },
          y: {
            beginAtZero: true,
            grid: {
              color: 'rgba(0, 0, 0, 0.1)'
            },
            ticks: {
              font: {
                size: 11
              }
            }
          }
        },
        elements: {
          bar: {
            borderRadius: 4,
            borderSkipped: false
          }
        }
      }
    }
  },
  computed: {
    getCurrentMonthName() {
      return this.currentDateSelected.toLocaleDateString("hu-HU", { month: "long" });
    },
    yearChartOptions() {
      return {
        ...this.baseChartOptions,
        plugins: {
          ...this.baseChartOptions.plugins,
          title: {
            display: false
          }
        }
      }
    },
    weekChartOptions() {
      return {
        ...this.baseChartOptions,
        plugins: {
          ...this.baseChartOptions.plugins,
          title: {
            display: false
          }
        }
      }
    }
  },
  mounted() {
    this.getStats();
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
      if (r.length == 1) r = "0" + r;
      if (g.length == 1) g = "0" + g;
      if (b.length == 1) b = "0" + b;

      return "#" + r + g + b;
    },
    async getStats() {
      try {
        const response = await this.orderStore.stats();

        if (response.status === 200) {
          // Process year data
          this.yearChartData.labels = response.data.data.year_data.labels;
          this.yearChartData.datasets = [];

          for (const [key, value] of Object.entries(response.data.data.year_data.data)) {
            this.yearChartData.datasets.push({
              label: key,
              backgroundColor: this.backgroundColor(key),
              borderColor: this.backgroundColor(key),
              borderWidth: 1,
              data: value.data,
              borderRadius: 4,
              borderSkipped: false
            });
          }
          this.vendorChartLoaded = true;

          // Process week data
          this.weekChartData.labels = response.data.data.week_data.labels;
          this.weekChartData.datasets = [];

          for (const [key, value] of Object.entries(response.data.data.week_data.data)) {
            this.weekChartData.datasets.push({
              label: key,
              backgroundColor: this.backgroundColor(key),
              borderColor: this.backgroundColor(key),
              borderWidth: 1,
              data: value.data,
              borderRadius: 4,
              borderSkipped: false
            });
          }
          this.weekChartLoaded = true;
        }
      } catch (error) {
        console.error('Error loading statistics:', error);
      }
    },
    getTotalVendors() {
      const allVendors = new Set();
      this.yearChartData.datasets.forEach(dataset => {
        allVendors.add(dataset.label);
      });
      this.weekChartData.datasets.forEach(dataset => {
        allVendors.add(dataset.label);
      });
      return allVendors.size;
    },
    getTotalYearOrders() {
      let total = 0;
      this.yearChartData.datasets.forEach(dataset => {
        total += dataset.data.reduce((sum, value) => sum + value, 0);
      });
      return total;
    },
    getTotalWeekOrders() {
      let total = 0;
      this.weekChartData.datasets.forEach(dataset => {
        total += dataset.data.reduce((sum, value) => sum + value, 0);
      });
      return total;
    },
    getAverageOrdersPerMonth() {
      const total = this.getTotalYearOrders();
      const monthsWithData = this.yearChartData.labels.length;
      return monthsWithData > 0 ? total / monthsWithData : 0;
    }
  }
}
</script>

<style scoped>
.chart-card {
  transition: all 0.3s ease;
  border-radius: 12px !important;
}

.chart-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
}

.chart-container {
  position: relative;
  height: 350px;
}

.v-card {
  border-radius: 12px !important;
}
/* Chart styling improvements */
.chart-container canvas {
  border-radius: 8px;
}

/* Summary cards styling */
.v-card[variant="tonal"] {
  transition: all 0.2s ease;
}

.v-card[variant="tonal"]:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
}
</style>
