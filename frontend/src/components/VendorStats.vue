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
                mdi-chart-line
              </v-icon>
              {{ vendorName }} — Statisztikák
            </h2>
          </v-col>
          <v-col cols="auto">
            <v-btn-toggle
              v-model="activeTab"
              mandatory
              color="white"
            >
              <v-btn value="inventory">
                <v-icon>mdi-package-variant</v-icon>
                <span class="ms-1 d-none d-sm-inline">{{ $t('stats.tab.inventory') }}</span>
              </v-btn>
              <v-btn value="sales">
                <v-icon>mdi-chart-bar</v-icon>
                <span class="ms-1 d-none d-sm-inline">{{ $t('stats.tab.sales') }}</span>
              </v-btn>
              <v-btn value="performance">
                <v-icon>mdi-trending-up</v-icon>
                <span class="ms-1 d-none d-sm-inline">{{ $t('stats.tab.performance') }}</span>
              </v-btn>
            </v-btn-toggle>
          </v-col>
        </v-row>
      </v-card-title>

      <v-card-text class="pa-4">
        <!-- ── TAB 1: INVENTORY ── -->
        <div v-show="activeTab === 'inventory'">
          <!-- Summary chips -->
          <v-row
            class="mb-4"
            dense
          >
            <v-col cols="auto">
              <v-chip
                color="error"
                prepend-icon="mdi-close-circle"
                variant="tonal"
              >
                {{ stockSummary.out_of_stock ?? '–' }} elfogyott
              </v-chip>
            </v-col>
            <v-col cols="auto">
              <v-chip
                color="warning"
                prepend-icon="mdi-alert"
                variant="tonal"
              >
                {{ stockSummary.low_stock ?? '–' }} alacsony
              </v-chip>
            </v-col>
            <v-col cols="auto">
              <v-chip
                color="secondary"
                prepend-icon="mdi-package-variant"
                variant="tonal"
              >
                {{ stockSummary.total_limited ?? '–' }} nyomon követett
              </v-chip>
            </v-col>
          </v-row>

          <!-- Category filter -->
          <v-row
            v-if="availableCategories.length > 0"
            class="mb-2"
            dense
          >
            <v-col
              cols="12"
              sm="4"
            >
              <v-select
                v-model="selectedCategory"
                :items="availableCategories"
                item-title="name"
                item-value="id"
                label="Kategória szűrő"
                density="compact"
                hide-details
                clearable
                placeholder="Összes kategória"
              />
            </v-col>
          </v-row>

          <v-row>
            <!-- Stock levels bar chart -->
            <v-col
              cols="12"
              lg="8"
            >
              <v-card
                variant="outlined"
                elevation="1"
              >
                <v-card-title class="text-subtitle-1 pa-3 bg-grey-lighten-5">
                  <v-icon
                    color="primary"
                    class="me-1"
                  >
                    mdi-package-variant
                  </v-icon>
                  {{ $t('stats.chart.stockLevels') }}
                </v-card-title>
                <v-card-text class="pa-3">
                  <div
                    v-if="stockLevelsLoading"
                    class="text-center py-8"
                  >
                    <v-progress-circular
                      indeterminate
                      color="primary"
                      size="48"
                    />
                  </div>
                  <div
                    v-else-if="stockChartData.labels.length === 0"
                    class="text-center text-grey py-6"
                  >
                    Nincs nyomon követett készlet.
                  </div>
                  <div
                    v-else
                    class="chart-container"
                  >
                    <Bar
                      :data="stockChartData"
                      :options="stockChartOptions"
                    />
                  </div>
                </v-card-text>
              </v-card>
            </v-col>

            <!-- Alerts list -->
            <v-col
              cols="12"
              lg="4"
            >
              <v-card
                variant="outlined"
                elevation="1"
                height="100%"
              >
                <v-card-title class="text-subtitle-1 pa-3 bg-grey-lighten-5">
                  <v-icon
                    color="warning"
                    class="me-1"
                  >
                    mdi-alert
                  </v-icon>
                  Figyelmeztetések
                </v-card-title>
                <v-card-text
                  class="pa-0"
                  style="max-height: 400px; overflow-y: auto;"
                >
                  <v-list density="compact">
                    <v-list-item
                      v-for="a in filteredStockAlerts"
                      :key="a.size_id"
                      :prepend-icon="alertIcon(a.alert_level)"
                      :title="a.item_name"
                      :subtitle="`${a.size_name} — ${a.quantity} db`"
                    >
                      <template #append>
                        <v-chip
                          :color="alertColor(a.alert_level)"
                          size="x-small"
                          variant="tonal"
                        >
                          {{ alertLabel(a.alert_level) }}
                        </v-chip>
                      </template>
                    </v-list-item>
                    <v-list-item v-if="filteredStockAlerts.length === 0">
                      <v-list-item-title class="text-center text-grey">
                        Nincs figyelmeztetés
                      </v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <!-- Depletion section -->
          <v-row class="mt-4">
            <v-col cols="12">
              <v-card
                variant="outlined"
                elevation="1"
              >
                <v-card-title class="text-subtitle-1 pa-3 bg-grey-lighten-5">
                  <v-icon
                    color="info"
                    class="me-1"
                  >
                    mdi-chart-timeline-variant
                  </v-icon>
                  Fogyás részletei
                </v-card-title>
                <v-card-text class="pa-2">
                  <!-- History date range filter -->
                  <v-row
                    dense
                    class="mb-3 px-2"
                  >
                    <v-col cols="auto">
                      <v-text-field
                        v-model="historyFrom"
                        type="date"
                        label="Előzmény dátumtól"
                        density="compact"
                        hide-details
                        clearable
                        style="min-width: 170px;"
                      />
                    </v-col>
                    <v-col cols="auto">
                      <v-text-field
                        v-model="historyTo"
                        type="date"
                        label="Előzmény dátumig"
                        density="compact"
                        hide-details
                        clearable
                        style="min-width: 170px;"
                      />
                    </v-col>
                    <v-col
                      cols="auto"
                      class="d-flex align-center"
                    >
                      <span class="text-caption text-grey">A dátumszűrő az előzmény betöltésekor érvényes.</span>
                    </v-col>
                  </v-row>
                  <div
                    v-if="stockLevelsLoading"
                    class="text-center py-4"
                  >
                    <v-progress-circular
                      indeterminate
                      color="primary"
                      size="32"
                    />
                  </div>
                  <div
                    v-else-if="filteredStockItems.length === 0"
                    class="text-center text-grey py-4"
                  >
                    Nincs adat.
                  </div>
                  <v-expansion-panels
                    v-else
                    variant="accordion"
                  >
                    <v-expansion-panel
                      v-for="item in filteredStockItems"
                      :key="item.item_id"
                    >
                      <v-expansion-panel-title @click="onItemPanelClick(item)">
                        <v-row
                          no-gutters
                          align="center"
                        >
                          <v-col>
                            <span class="font-weight-medium">{{ item.item_name }}</span>
                            <span class="text-caption text-grey ms-2">{{ item.category_name }}</span>
                          </v-col>
                          <v-col cols="auto">
                            <v-chip
                              size="x-small"
                              variant="flat"
                              color="secondary"
                              class="me-2"
                            >
                              {{ item.sizes.reduce((s, sz) => s + sz.quantity, 0) }} db
                            </v-chip>
                          </v-col>
                        </v-row>
                      </v-expansion-panel-title>
                      <v-expansion-panel-text>
                        <div
                          v-for="sz in item.sizes"
                          :key="sz.size_id"
                          class="mb-4"
                        >
                          <v-row
                            align="center"
                            class="mb-2"
                          >
                            <v-col>
                              <span class="text-body-2 font-weight-medium">{{ sz.size_name }}</span>
                              <v-chip
                                :color="sz.quantity === 0 ? 'error' : sz.quantity < 10 ? 'warning' : 'success'"
                                size="x-small"
                                variant="tonal"
                                class="ms-2"
                              >
                                {{ sz.quantity }} db
                              </v-chip>
                            </v-col>
                            <v-col
                              cols="auto"
                              class="d-flex align-center"
                              style="gap: 8px;"
                            >
                              <v-btn
                                size="x-small"
                                variant="text"
                                color="primary"
                                @click="loadSizeHistory(sz.size_id)"
                              >
                                Frissítés
                              </v-btn>
                              <v-btn
                                size="small"
                                variant="tonal"
                                color="success"
                                prepend-icon="mdi-plus-circle"
                                @click="openTopup(sz.size_id, sz.size_name, item.item_name)"
                              >
                                Feltöltés
                              </v-btn>
                            </v-col>
                          </v-row>
                          <!-- Depletion history -->
                          <div v-if="sizeHistories[sz.size_id]">
                            <div
                              v-if="sizeHistories[sz.size_id].loading"
                              class="text-center py-2"
                            >
                              <v-progress-circular
                                indeterminate
                                color="primary"
                                size="24"
                              />
                            </div>
                            <template v-else>
                              <div
                                v-if="sizeHistories[sz.size_id].chartData"
                                class="chart-container-sm"
                              >
                                <Line
                                  :data="sizeHistories[sz.size_id].chartData"
                                  :options="depletionChartOptions"
                                />
                                <div class="text-caption text-grey mt-1 ps-1">
                                  <span class="me-4">&#9679; <span style="color:#1976d2;">Kék</span> = rendelés</span>
                                  <span>&#9679; <span style="color:#4caf50;">Zöld</span> = feltöltés</span>
                                </div>
                              </div>
                              <!-- History entries table -->
                              <v-table
                                v-if="sizeHistories[sz.size_id].entries.length"
                                density="compact"
                                class="mt-3"
                              >
                                <thead>
                                  <tr>
                                    <th>Időpont</th>
                                    <th>Változás</th>
                                    <th>Ok</th>
                                    <th>Megjegyzés</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  <tr
                                    v-for="e in sizeHistories[sz.size_id].entries"
                                    :key="e.id"
                                  >
                                    <td class="text-caption">
                                      {{ formatTimestamp(e.timestamp) }}
                                    </td>
                                    <td>
                                      <span
                                        :class="e.quantity_change > 0 ? 'text-success' : 'text-error'"
                                        class="font-weight-bold"
                                      >
                                        {{ e.quantity_change > 0 ? '+' : '' }}{{ e.quantity_change }}
                                      </span>
                                    </td>
                                    <td class="text-caption">
                                      {{ reasonLabel(e.reason) }}
                                    </td>
                                    <td class="text-caption">
                                      {{ e.note || '–' }}
                                    </td>
                                  </tr>
                                </tbody>
                              </v-table>
                              <div
                                v-else-if="!sizeHistories[sz.size_id].chartData"
                                class="text-caption text-grey text-center py-2"
                              >
                                Nincs előzmény.
                              </div>
                            </template>
                          </div>
                        </div>
                      </v-expansion-panel-text>
                    </v-expansion-panel>
                  </v-expansion-panels>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <!-- Bulk depletion rate section -->
          <v-row class="mt-4">
            <v-col cols="12">
              <v-card
                variant="outlined"
                elevation="1"
              >
                <v-card-title class="text-subtitle-1 pa-3 bg-grey-lighten-5">
                  <v-icon
                    color="info"
                    class="me-1"
                  >
                    mdi-speedometer
                  </v-icon>
                  Fogyási sebesség
                </v-card-title>
                <v-card-text class="pa-2">
                  <v-row
                    dense
                    class="mb-3 px-2"
                  >
                    <v-col cols="auto">
                      <v-text-field
                        v-model="depletionRateFrom"
                        type="date"
                        label="Dátumtól"
                        density="compact"
                        hide-details
                        clearable
                        style="min-width: 170px;"
                      />
                    </v-col>
                    <v-col cols="auto">
                      <v-text-field
                        v-model="depletionRateTo"
                        type="date"
                        label="Dátumig"
                        density="compact"
                        hide-details
                        clearable
                        style="min-width: 170px;"
                      />
                    </v-col>
                    <v-col
                      cols="auto"
                      class="d-flex align-center"
                    >
                      <v-btn
                        size="small"
                        color="primary"
                        variant="tonal"
                        @click="loadDepletionRates"
                      >
                        Frissítés
                      </v-btn>
                    </v-col>
                  </v-row>
                  <div
                    v-if="depletionRatesLoading"
                    class="text-center py-4"
                  >
                    <v-progress-circular
                      indeterminate
                      color="primary"
                      size="32"
                    />
                  </div>
                  <v-data-table
                    v-else
                    :headers="depletionHeaders"
                    :items="depletionRates"
                    :sort-by="[{ key: 'per_day', order: 'desc' }]"
                    density="compact"
                    class="elevation-0"
                    no-data-text="Nincs adat a kiválasztott időszakban."
                  />
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </div>

        <!-- ── TAB 2: SALES ── -->
        <div v-show="activeTab === 'sales'">
          <!-- Preset filter -->
          <v-row
            class="mb-4"
            justify="center"
          >
            <v-col cols="auto">
              <v-btn-toggle
                v-model="salesPreset"
                mandatory
                color="primary"
                @update:model-value="onPresetChange"
              >
                <v-btn
                  value="last_30_days"
                  size="small"
                >
                  {{ $t('stats.preset.last30') }}
                </v-btn>
                <v-btn
                  value="current_month"
                  size="small"
                >
                  {{ $t('stats.preset.currentMonth') }}
                </v-btn>
                <v-btn
                  value="last_month"
                  size="small"
                >
                  {{ $t('stats.preset.lastMonth') }}
                </v-btn>
                <v-btn
                  value="since_last_topup"
                  size="small"
                >
                  {{ $t('stats.preset.sinceLastTopup') }}
                </v-btn>
                <v-btn
                  value="all_time"
                  size="small"
                >
                  {{ $t('stats.preset.allTime') }}
                </v-btn>
              </v-btn-toggle>
            </v-col>
          </v-row>

          <v-row>
            <!-- Revenue trend line chart -->
            <v-col
              cols="12"
              lg="6"
            >
              <v-card
                variant="outlined"
                elevation="1"
              >
                <v-card-title class="text-subtitle-1 pa-3 bg-grey-lighten-5">
                  <v-icon
                    color="primary"
                    class="me-1"
                  >
                    mdi-chart-line
                  </v-icon>
                  {{ $t('stats.chart.salesTrend') }}
                </v-card-title>
                <v-card-text class="pa-3">
                  <div
                    v-if="salesTrendRangeLabel"
                    class="text-caption text-grey mb-2"
                  >
                    {{ salesTrendRangeLabel }}
                  </div>
                  <div
                    v-if="salesLoading"
                    class="text-center py-8"
                  >
                    <v-progress-circular
                      indeterminate
                      color="primary"
                      size="48"
                    />
                  </div>
                  <div
                    v-else
                    class="chart-container"
                  >
                    <Line
                      :data="salesTrendChartData"
                      :options="salesTrendChartOptions"
                    />
                  </div>
                </v-card-text>
              </v-card>
            </v-col>

            <!-- Popular items doughnut -->
            <v-col
              cols="12"
              lg="6"
            >
              <v-card
                variant="outlined"
                elevation="1"
              >
                <v-card-title class="text-subtitle-1 pa-3 bg-grey-lighten-5">
                  <v-icon
                    color="primary"
                    class="me-1"
                  >
                    mdi-fire
                  </v-icon>
                  {{ $t('stats.chart.popularItems') }}
                </v-card-title>
                <v-card-text class="pa-3">
                  <div
                    v-if="salesLoading"
                    class="text-center py-8"
                  >
                    <v-progress-circular
                      indeterminate
                      color="primary"
                      size="48"
                    />
                  </div>
                  <div
                    v-else-if="popularChartData.labels.length === 0"
                    class="text-center text-grey py-6"
                  >
                    Nincs adat.
                  </div>
                  <div
                    v-else
                    class="chart-container"
                  >
                    <Doughnut
                      :data="popularChartData"
                      :options="popularChartOptions"
                    />
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <!-- Per-user spend table -->
          <v-row class="mt-4">
            <v-col cols="12">
              <v-card
                variant="outlined"
                elevation="1"
              >
                <v-card-title class="text-subtitle-1 pa-3 bg-grey-lighten-5">
                  <v-icon
                    color="primary"
                    class="me-1"
                  >
                    mdi-account-group
                  </v-icon>
                  Felhasználónkénti költés
                </v-card-title>
                <v-data-table
                  :headers="spendHeaders"
                  :items="perUserSpend"
                  :loading="salesLoading"
                  density="compact"
                  class="elevation-0"
                >
                  <template #item.total_spend="{ item }">
                    {{ formatFt(item.total_spend) }}
                  </template>
                </v-data-table>
              </v-card>
            </v-col>
          </v-row>
        </div>

        <!-- ── TAB 3: PERFORMANCE ── -->
        <div v-show="activeTab === 'performance'">
          <!-- KPI cards -->
          <v-row
            class="mb-4"
            dense
          >
            <v-col
              cols="12"
              sm="6"
              md="3"
            >
              <v-card
                variant="tonal"
                color="primary"
                class="text-center pa-3"
              >
                <v-icon
                  size="28"
                  class="mb-1"
                >
                  mdi-currency-usd
                </v-icon>
                <div class="text-h6 font-weight-bold">
                  {{ formatFt(kpiSummary.total_revenue) }}
                </div>
                <div class="text-body-2">
                  {{ $t('stats.kpi.totalRevenue') }}
                </div>
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
                class="text-center pa-3"
              >
                <v-icon
                  size="28"
                  class="mb-1"
                >
                  mdi-receipt
                </v-icon>
                <div class="text-h6 font-weight-bold">
                  {{ formatFt(kpiSummary.avg_order_value) }}
                </div>
                <div class="text-body-2">
                  {{ $t('stats.kpi.avgOrderValue') }}
                </div>
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
                class="text-center pa-3"
              >
                <v-icon
                  size="28"
                  class="mb-1"
                >
                  mdi-calendar-today
                </v-icon>
                <div class="text-h6 font-weight-bold">
                  {{ kpiSummary.orders_per_day ?? '–' }}
                </div>
                <div class="text-body-2">
                  {{ $t('stats.kpi.ordersPerDay') }}
                </div>
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
                class="text-center pa-3"
              >
                <v-icon
                  size="28"
                  class="mb-1"
                >
                  mdi-fire
                </v-icon>
                <div class="text-subtitle-1 font-weight-bold text-truncate">
                  {{ kpiSummary.most_popular_item ?? '–' }}
                </div>
                <div class="text-body-2">
                  {{ $t('stats.kpi.mostPopular') }}
                </div>
              </v-card>
            </v-col>
          </v-row>

          <!-- Vendor trend bar chart -->
          <v-card
            variant="outlined"
            elevation="1"
          >
            <v-card-title class="text-subtitle-1 pa-3 bg-grey-lighten-5">
              <v-icon
                color="primary"
                class="me-1"
              >
                mdi-chart-bar
              </v-icon>
              {{ $t('stats.chart.vendorTrend') }}
            </v-card-title>
            <v-card-text class="pa-3">
              <v-row
                dense
                class="mb-3"
              >
                <v-col cols="auto">
                  <v-text-field
                    v-model="vendorTrendFrom"
                    type="date"
                    label="Dátumtól"
                    density="compact"
                    hide-details
                    clearable
                    style="min-width: 170px;"
                  />
                </v-col>
                <v-col cols="auto">
                  <v-text-field
                    v-model="vendorTrendTo"
                    type="date"
                    label="Dátumig"
                    density="compact"
                    hide-details
                    clearable
                    style="min-width: 170px;"
                  />
                </v-col>
                <v-col
                  cols="auto"
                  class="d-flex align-center"
                >
                  <v-btn
                    size="small"
                    color="primary"
                    variant="tonal"
                    @click="loadVendorTrend"
                  >
                    Frissítés
                  </v-btn>
                </v-col>
              </v-row>
              <div
                v-if="performanceLoading"
                class="text-center py-8"
              >
                <v-progress-circular
                  indeterminate
                  color="primary"
                  size="48"
                />
              </div>
              <div
                v-else
                class="chart-container"
              >
                <Bar
                  :data="vendorTrendChartData"
                  :options="vendorTrendChartOptions"
                />
              </div>
            </v-card-text>
          </v-card>
        </div>
      </v-card-text>
    </v-card>

    <!-- Top-up dialog -->
    <v-dialog
      v-model="topupDialog.open"
      max-width="400"
    >
      <v-card>
        <v-card-title>{{ $t('stats.topup.title') }} — {{ topupDialog.itemName }} ({{ topupDialog.sizeName }})</v-card-title>
        <v-card-text>
          <v-text-field
            v-model.number="topupForm.quantity"
            :label="$t('stats.topup.quantity')"
            type="number"
            min="1"
            :rules="[v => v > 0 || 'Legalább 1']"
          />
          <v-text-field
            v-model="topupForm.note"
            :label="$t('stats.topup.note')"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="topupDialog.open = false"
          >
            Mégse
          </v-btn>
          <v-btn
            color="success"
            variant="tonal"
            :loading="topupLoading"
            :disabled="!topupForm.quantity || topupForm.quantity < 1"
            @click="confirmTopup"
          >
            {{ $t('stats.topup.confirm') }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Title,
  Tooltip,
} from 'chart.js';
import { Bar, Doughnut, Line } from 'vue-chartjs';
import { useStatsStore } from '@/stores/stats';
import axios from 'axios';

ChartJS.register(
  Title, Tooltip, Legend,
  BarElement, CategoryScale, LinearScale,
  LineElement, PointElement, ArcElement,
);

const DOUGHNUT_COLORS = [
  '#FF6384', '#36A2EB', '#FFCD56', '#4BC0C0', '#9966FF',
  '#FF9F40', '#C9CBCF', '#7BC8A4', '#EA80FC', '#F48FB1',
];

export default {
  name: 'VendorStats',
  // eslint-disable-next-line vue/no-reserved-component-names
  components: { Bar, Line, Doughnut },

  setup() {
    return { statsStore: useStatsStore() };
  },

  data() {
    return {
      activeTab: 'inventory',
      vendorName: '',
      vendorId: null,

      // Inventory tab
      stockSummary: {},
      stockAlerts: [],
      stockItems: [],
      stockLevelsLoading: false,
      sizeHistories: {},   // { [size_id]: { loading, chartData, entries } }
      historyFrom: '',
      historyTo: '',
      selectedCategory: null,
      vendorTrendFrom: '',
      vendorTrendTo: '',
      depletionRates: [],
      depletionRatesLoading: false,
      depletionRateFrom: '',
      depletionRateTo: '',
      depletionHeaders: [],

      // Sales tab
      salesPreset: 'last_30_days',
      salesLoading: false,
      salesTrendRaw: [],
      salesTrendFrom: null,
      salesTrendTo: null,
      popularItemsRaw: [],
      perUserSpend: [],

      // Performance tab
      performanceLoading: false,
      kpiSummary: {},
      vendorTrendRaw: [],

      // Topup dialog
      topupDialog: { open: false, sizeId: null, sizeName: '', itemName: '' },
      topupForm: { quantity: null, note: '' },
      topupLoading: false,

      spendHeaders: [],

      depletionChartOptions: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { font: { size: 10 } } },
          y: { beginAtZero: false, ticks: { font: { size: 10 } } },
        },
      },
    };
  },

  computed: {
    stockChartData() {
      const labels = [];
      const data = [];
      const colors = [];
      for (const item of this.filteredStockItems) {
        for (const sz of item.sizes) {
          labels.push(`${item.item_name} (${sz.size_name})`);
          data.push(sz.quantity);
          colors.push(sz.quantity === 0 ? '#f44336' : sz.quantity < 10 ? '#ff9800' : '#4caf50');
        }
      }
      return {
        labels,
        datasets: [{ label: 'Készlet (db)', data, backgroundColor: colors, borderWidth: 0 }],
      };
    },

    stockChartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { font: { size: 10 }, maxRotation: 45 } },
          y: { beginAtZero: true, title: { display: true, text: 'db' } },
        },
      };
    },

    salesTrendChartData() {
      return {
        labels: this.salesTrendRaw.map(d => d.date),
        datasets: [{
          label: 'Bevétel (Ft)',
          data: this.salesTrendRaw.map(d => d.revenue),
          borderColor: '#1976d2',
          backgroundColor: 'rgba(25,118,210,0.1)',
          fill: true,
          tension: 0.4,
          pointRadius: 3,
        }],
      };
    },

    salesTrendChartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { font: { size: 10 }, maxRotation: 45 } },
          y: { beginAtZero: true, title: { display: true, text: 'Ft' } },
        },
      };
    },

    popularChartData() {
      return {
        labels: this.popularItemsRaw.map(i => i.name),
        datasets: [{
          data: this.popularItemsRaw.map(i => i.count),
          backgroundColor: DOUGHNUT_COLORS.slice(0, this.popularItemsRaw.length),
        }],
      };
    },

    popularChartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: { position: 'right', labels: { font: { size: 11 } } },
          tooltip: {
            callbacks: {
              label: ctx => `${ctx.label}: ${ctx.parsed} db`,
            },
          },
        },
      };
    },

    vendorTrendChartData() {
      return {
        labels: this.vendorTrendRaw.map(r => r.period_label),
        datasets: [{
          label: 'Rendelések',
          data: this.vendorTrendRaw.map(r => r.order_count),
          backgroundColor: '#1976d2',
          borderRadius: 4,
        }],
      };
    },

    vendorTrendChartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { font: { size: 11 } } },
          y: { beginAtZero: true, title: { display: true, text: 'Rendelések' } },
        },
      };
    },

    salesTrendRangeLabel() {
      if (!this.salesTrendTo) return '';
      const fmt = d => new Date(d).toLocaleDateString('hu-HU');
      const from = this.salesTrendFrom ? fmt(this.salesTrendFrom) : '–';
      return `Időszak: ${from} – ${fmt(this.salesTrendTo)}`;
    },

    availableCategories() {
      const seen = new Map();
      for (const item of this.stockItems) {
        if (item.category_id != null && !seen.has(item.category_id)) {
          seen.set(item.category_id, item.category_name || 'Kategória nélkül');
        }
      }
      return Array.from(seen, ([id, name]) => ({ id, name }));
    },

    filteredStockItems() {
      if (this.selectedCategory == null) return this.stockItems;
      return this.stockItems.filter(i => i.category_id === this.selectedCategory);
    },

    filteredStockAlerts() {
      if (this.selectedCategory == null) return this.stockAlerts;
      const sizeIds = new Set(
        this.filteredStockItems.flatMap(i => i.sizes.map(s => s.size_id))
      );
      return this.stockAlerts.filter(a => sizeIds.has(a.size_id));
    },
  },

  async mounted() {
    this.vendorId = this.$route.params.vendorId;
    this.spendHeaders = [
      { title: this.$t('stats.table.user'), key: 'username', sortable: true },
      { title: this.$t('stats.table.totalSpend'), key: 'total_spend', sortable: true },
      { title: this.$t('stats.table.orderCount'), key: 'order_count', sortable: true },
    ];
    this.depletionHeaders = [
      { title: 'Termék', key: 'item_name', sortable: true },
      { title: 'Méret', key: 'size_name', sortable: true },
      { title: 'Fogyott (db)', key: 'total_depleted', sortable: true },
      { title: 'db / nap', key: 'per_day', sortable: true },
    ];
    await this.loadVendorInfo();
    await Promise.all([
      this.loadInventoryTab(),
      this.loadSalesTab(),
      this.loadPerformanceTab(),
    ]);
  },

  methods: {
    async loadVendorInfo() {
      try {
        const res = await axios.get(`/api/vendor/${this.vendorId}`);
        this.vendorName = res.data?.data?.name ?? '';
      } catch {
        // non-critical
      }
    },

    async loadInventoryTab() {
      this.stockLevelsLoading = true;
      try {
        const [summary, alerts, items] = await Promise.all([
          this.statsStore.fetchKpiSummary(this.vendorId),
          this.statsStore.fetchStockAlerts(this.vendorId),
          axios.get(`/api/vendor/${this.vendorId}/stock`).then(r => r.data.data.items),
        ]);
        this.stockSummary = {
          out_of_stock: summary.out_of_stock,
          low_stock: summary.low_stock,
          total_limited: summary.total_limited,
        };
        this.stockAlerts = alerts;
        this.stockItems = items;
      } catch (e) {
        console.error('Inventory load error:', e);
      } finally {
        this.stockLevelsLoading = false;
      }
      await this.loadDepletionRates();
    },

    async loadDepletionRates() {
      this.depletionRatesLoading = true;
      try {
        const params = {};
        if (this.depletionRateFrom) params.from = this.depletionRateFrom;
        if (this.depletionRateTo) params.to = this.depletionRateTo;
        this.depletionRates = await this.statsStore.fetchDepletionRates(this.vendorId, params);
      } catch (e) {
        console.error('Depletion rates load error:', e);
      } finally {
        this.depletionRatesLoading = false;
      }
    },

    async loadSalesTab() {
      this.salesLoading = true;
      try {
        const preset = this.salesPreset;
        const [trend, popular, spend] = await Promise.all([
          this.statsStore.fetchSalesTrend(this.vendorId, { preset }),
          this.statsStore.fetchPopularItems(this.vendorId, { preset }),
          this.statsStore.fetchPerUserSpend(this.vendorId, { preset }),
        ]);
        this.salesTrendRaw = trend.sales;
        this.salesTrendFrom = trend.from_date;
        this.salesTrendTo = trend.to_date;
        this.popularItemsRaw = popular;
        this.perUserSpend = spend;
      } catch (e) {
        console.error('Sales load error:', e);
      } finally {
        this.salesLoading = false;
      }
    },

    async loadPerformanceTab() {
      this.performanceLoading = true;
      try {
        const params = {};
        if (this.vendorTrendFrom) params.from = this.vendorTrendFrom;
        if (this.vendorTrendTo) params.to = this.vendorTrendTo;
        const [kpi, trend] = await Promise.all([
          this.statsStore.fetchKpiSummary(this.vendorId),
          this.statsStore.fetchVendorTrend(this.vendorId, params),
        ]);
        this.kpiSummary = kpi;
        this.vendorTrendRaw = trend;
      } catch (e) {
        console.error('Performance load error:', e);
      } finally {
        this.performanceLoading = false;
      }
    },

    async loadVendorTrend() {
      this.performanceLoading = true;
      try {
        const params = {};
        if (this.vendorTrendFrom) params.from = this.vendorTrendFrom;
        if (this.vendorTrendTo) params.to = this.vendorTrendTo;
        this.vendorTrendRaw = await this.statsStore.fetchVendorTrend(this.vendorId, params);
      } catch (e) {
        console.error('Vendor trend load error:', e);
      } finally {
        this.performanceLoading = false;
      }
    },

    async onPresetChange() {
      await this.loadSalesTab();
    },

    async loadSizeHistory(sizeId) {
      this.sizeHistories[sizeId] = { loading: true, chartData: null, entries: [] };
      try {
        const params = {};
        if (this.historyFrom) params.from = this.historyFrom;
        if (this.historyTo) params.to = this.historyTo;
        const data = await this.statsStore.fetchStockHistory(sizeId, params);
        this.sizeHistories[sizeId] = {
          loading: false,
          chartData: this.buildDepletionChart(data),
          entries: data.history || [],
        };
      } catch {
        this.sizeHistories[sizeId] = { loading: false, chartData: null, entries: [] };
      }
    },

    buildDepletionChart({ anchor_quantity, history }) {
      if (!history || history.length === 0) return null;

      const labels = [];
      const quantities = [];
      const pointColors = [];
      const pointRadii = [];

      let running = anchor_quantity;
      for (const entry of history) {
        running += entry.quantity_change;
        labels.push(new Date(entry.timestamp).toLocaleDateString('hu-HU'));
        quantities.push(running);
        const isTopup = entry.reason === 'topup';
        pointColors.push(isTopup ? '#4caf50' : '#1976d2');
        pointRadii.push(isTopup ? 6 : 3);
      }

      return {
        labels,
        datasets: [{
          label: 'Készlet',
          data: quantities,
          borderColor: '#1976d2',
          backgroundColor: 'transparent',
          tension: 0.1,
          pointBackgroundColor: pointColors,
          pointRadius: pointRadii,
        }],
      };
    },

    openTopup(sizeId, sizeName, itemName) {
      this.topupDialog = { open: true, sizeId, sizeName, itemName };
      this.topupForm = { quantity: null, note: '' };
    },

    async confirmTopup() {
      if (!this.topupForm.quantity || this.topupForm.quantity < 1) return;
      this.topupLoading = true;
      const sizeId = this.topupDialog.sizeId;
      const addedQty = this.topupForm.quantity;
      try {
        await this.statsStore.topUpStock(sizeId, addedQty, this.topupForm.note);
        this.topupDialog.open = false;
        // Update quantity in-place so scroll position is preserved
        for (const item of this.stockItems) {
          const sz = item.sizes.find(s => s.size_id === sizeId);
          if (sz) { sz.quantity += addedQty; break; }
        }
        // Refresh only summary chips + alerts (lightweight)
        await this._refreshSummaryAndAlerts();
        // Refresh depletion history if already loaded
        if (this.sizeHistories[sizeId]) {
          await this.loadSizeHistory(sizeId);
        }
      } catch (e) {
        console.error('Top-up failed:', e);
      } finally {
        this.topupLoading = false;
      }
    },

    onItemPanelClick(item) {
      for (const sz of item.sizes) {
        if (!this.sizeHistories[sz.size_id]) {
          this.loadSizeHistory(sz.size_id);
        }
      }
    },

    async _refreshSummaryAndAlerts() {
      try {
        const [summary, alerts] = await Promise.all([
          this.statsStore.fetchKpiSummary(this.vendorId),
          this.statsStore.fetchStockAlerts(this.vendorId),
        ]);
        this.stockSummary = {
          out_of_stock: summary.out_of_stock,
          low_stock: summary.low_stock,
          total_limited: summary.total_limited,
        };
        this.stockAlerts = alerts;
      } catch (e) {
        console.error('Summary/alerts refresh error:', e);
      }
    },

    reasonLabel(reason) {
      if (reason === 'order') return 'Rendelés';
      if (reason === 'topup') return 'Feltöltés';
      if (reason === 'adjustment') return 'Kézi módosítás';
      return reason;
    },

    formatTimestamp(ts) {
      return new Date(ts).toLocaleString('hu-HU');
    },

    alertColor(level) {
      return level === 'out_of_stock' ? 'error' : level === 'critical' ? 'deep-orange' : 'warning';
    },

    alertIcon(level) {
      return level === 'out_of_stock' ? 'mdi-close-circle' : level === 'critical' ? 'mdi-alert-circle' : 'mdi-alert';
    },

    alertLabel(level) {
      if (level === 'out_of_stock') return this.$t('stats.alert.outOfStock');
      if (level === 'critical') return this.$t('stats.alert.critical');
      return this.$t('stats.alert.low');
    },

    formatFt(value) {
      if (value == null) return '–';
      return new Intl.NumberFormat('hu-HU').format(Math.round(value)) + ' Ft';
    },
  },
};
</script>

<style scoped>
.chart-container {
  position: relative;
  height: 320px;
}

.chart-container-sm {
  position: relative;
  height: 180px;
}
</style>
