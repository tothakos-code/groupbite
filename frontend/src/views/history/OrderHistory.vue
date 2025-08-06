<template>
  <v-container
    fluid
    max-width="1400"
  >
    <div className="mb-8">
      <h2 className="text-h4 mb-4">
        Rendelés történeted
      </h2>
      <p className="text-gray-600">
        Előző rendeléseid és statisztikáid
      </p>
    </div>
    <UserStatistics :user-id="auth.user.id" />
    <!-- Search and Filter Section -->
    <v-card
      class="mb-4"
      elevation="1"
    >
      <v-card-text>
        <v-row>
          <!-- Search Input -->
          <v-col
            cols="12"
            md="6"
          >
            <v-text-field
              v-model="searchQuery"
              label="Keresés..."
              placeholder="Keress étel névre, rendelésre, vagy üzletre"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="compact"
              clearable
              @input="debounceSearch"
            />
          </v-col>

          <!-- Vendor Filter -->
          <v-col
            cols="12"
            md="4"
          >
            <v-select
              v-model="selectedVendor"
              :items="vendorOptions"
              item-value="id"
              label="Üzlet szűrése"
              variant="outlined"
              density="compact"
              clearable
              prepend-inner-icon="mdi-store"
              @update:model-value="applyFilters"
            />
          </v-col>

          <!-- Date Range Filter -->
          <v-col
            cols="12"
            md="2"
          >
            <v-menu
              v-model="dateMenu"
              :close-on-content-click="false"
              transition="scale-transition"
              offset-y
              min-width="auto"
            >
              <template #activator="{ props }">
                <v-btn
                  v-bind="props"
                  variant="outlined"
                  color="primary"
                  size="small"
                  block
                >
                  <v-icon
                    small
                    class="mr-1"
                  >
                    mdi-calendar
                  </v-icon>
                  Dátum tartomány
                </v-btn>
              </template>
              <v-card>
                <v-card-text>
                  <v-date-picker
                    v-model="dateRange"
                    multiple="range"
                    title="Dátum szűrés"
                    @update:model-value="applyDateFilter"
                  />
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn
                    text
                    @click="clearDateFilter"
                  >
                    Üres
                  </v-btn>
                  <v-btn
                    text
                    @click="dateMenu = false"
                  >
                    Bezár
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-menu>
          </v-col>
        </v-row>

        <!-- Active Filters -->
        <div
          v-if="hasActiveFilters"
          class="mt-3"
        >
          <v-chip-group>
            <v-chip
              v-if="searchQuery"
              closable
              color="primary"
              variant="outlined"
              @click:close="clearSearch"
            >
              <v-icon
                small
                class="mr-1"
              >
                mdi-magnify
              </v-icon>
              Keresés: "{{ searchQuery }}"
            </v-chip>

            <v-chip
              v-if="selectedVendor"
              closable
              color="primary"
              variant="outlined"
              @click:close="clearVendorFilter"
            >
              <v-icon
                small
                class="mr-1"
              >
                mdi-store
              </v-icon>
              {{ getVendorName(selectedVendor) }}
            </v-chip>

            <v-chip
              v-if="dateRange && dateRange.length > 1"
              closable
              color="primary"
              variant="outlined"
              @click:close="clearDateFilter"
            >
              <v-icon
                small
                class="mr-1"
              >
                mdi-calendar
              </v-icon>
              {{ formatDateRange(dateRange) }}
            </v-chip>

            <v-chip
              v-if="hasActiveFilters"
              color="error"
              variant="outlined"
              @click="clearAllFilters"
            >
              <v-icon
                small
                class="mr-1"
              >
                mdi-close
              </v-icon>
              Szűrések törlése
            </v-chip>
          </v-chip-group>
        </div>
      </v-card-text>
    </v-card>
    <v-skeleton-loader
      v-if="isLoading"
      type="card@3"
      class="mx-auto"
    />
    <v-card
      v-else-if="orderHistoryList.length === 0"
      class="text-center pa-8"
    >
      <v-icon
        size="64"
        color="grey-lighten-1"
        class="mb-4"
      >
        mdi-receipt-text-outline
      </v-icon>
      <h3 class="text-h5 mb-2">
        {{ hasActiveFilters ? "No Orders found" : "No Orders Yet" }}
      </h3>
      <p class="text-body-1 grey--text">
        {{ hasActiveFilters ? "No orders with the selected filtes" : "Start ordering to see your history here!" }}
      </p>
    </v-card>
    <div
      v-else
      class=""
    >
      <v-card
        v-for="order in orderHistoryList"
        :key="order.id"
        class="mb-4"
        elevation="2"
        max-width="1400"
      >
        <v-card-title class="d-flex justify-space-between align-center">
          <div>
            <h3 class="text-h6">
              Rendelés azonosító #{{ order.id }}
            </h3>
            <p class="text-caption mb-0 grey--text">
              {{ formatDate(order.date_of_order) }}
              <span v-if="order.order_time">
                at {{ formatTime(order.order_time) }}
              </span>
            </p>
          </div>
          <v-chip
            small
            :class="{
              'bg-success': order.state_id === 'collect',
              'bg-warning': order.state_id === 'order',
              'bg-error': order.state_id === 'closed'}"
          >
            {{ order.state_id }}
          </v-chip>
        </v-card-title>

        <v-divider />

        <v-card-text>
          <!-- Vendor Info -->
          <div class="mb-3">
            <v-icon
              small
              class="mr-2"
            >
              mdi-store
            </v-icon>
            <span class="font-weight-medium">{{ order.vendor?.name || 'Unknown Vendor' }}</span>
          </div>

          <!-- Order Items -->
          <v-expansion-panels
            v-model="expandedPanels[order.id]"
            flat
          >
            <v-expansion-panel>
              <v-expansion-panel-title>
                <div class="d-flex justify-space-between align-center w-100">
                  <span>
                    <v-icon
                      small
                      class="mr-2"
                    >mdi-food</v-icon>
                    {{ order.order_items.length }} tétel{{ order.order_items.length !== 1 ? 's' : '' }}
                  </span>
                  <span class="text-right">
                    <strong>{{ Math.ceil(order.total_price) }} Ft</strong>
                  </span>
                </div>
              </v-expansion-panel-title>

              <v-expansion-panel-text>
                <v-list dense>
                  <v-list-item
                    v-for="item in order.order_items"
                    :key="item.id"
                    class="px-0"
                  >
                    <div class="d-flex justify-space-between align-center">
                      <div>
                        <v-list-item-title class="font-weight-medium">
                          {{ item.item_name }}
                        </v-list-item-title>
                        <v-list-item-subtitle>
                          Size: {{ item.size_label }}
                          <span v-if="item.count > 1">
                            • Quantity: {{ item.count }}
                          </span>
                        </v-list-item-subtitle>
                      </div>
                      <div class="text-right">
                        <div class="font-weight-medium">
                          {{ item.total_price }} Ft
                        </div>
                        <div class="text-caption grey--text">
                          {{ item.unit_price }} Ft/db
                        </div>
                      </div>
                    </div>
                  </v-list-item>
                </v-list>

                <!-- Order Summary -->
                <v-divider class="my-3" />
                <div class="d-flex justify-space-between">
                  <div>
                    <div v-if="order.order_fee > 0">
                      <span>Részösszeg: {{ order.total_price - order.order_fee }} Ft</span><br>
                      <span>Szállítási díj: {{ order.order_fee }} Ft</span><br>
                    </div>
                    <span class="font-weight-bold">Összesen: {{ order.total_price }} Ft</span>
                  </div>
                </div>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-card-text>
      </v-card>
      <Paginator
        :total-pages="Math.ceil(totalCount/limit)"
        :current-page="currentPage"
        :range="5"
        @page-change="handlePageChange"
      />
    </div>
  </v-container>
</template>

<script>
import UserStatistics from "@/components/UserStatistics.vue";
import Paginator from "@/components/Paginator.vue";
import { useAuth } from "@/stores/auth.js";
import { reactive } from 'vue'

export default {
  name: "UserMenu",
  components: {
    UserStatistics,
    Paginator
  },
  setup() {
    const auth = useAuth();
    return {
      auth
    }
  },
  data() {
    return {
      orderHistoryList: [],
      isLoading: true,
      limit: 10,
      currentPage: 1,
      totalCount: 0,
      expandedPanels: reactive({}),
      searchQuery: "",
      selectedVendor: null,
      vendorOptions: [],
      dateRange: [],
      dateMenu: false,
      searchTimeout: null
    }
  },
  computed: {
    hasActiveFilters() {
      return this.searchQuery || this.selectedVendor || (this.dateRange && this.dateRange.length > 1)
    },

  },
  mounted() {
    this.loadUserHistory()
  },
  methods: {
    handlePageChange(page) {
      this.currentPage = page;
      this.loadUserHistory()
    },
    loadUserHistory() {
      let params = {
          "limit": this.limit,
          "page": this.currentPage
        }
      if (this.searchQuery) params['search'] =  this.searchQuery
      if (this.selectedVendor) params['vendor_id'] = this.selectedVendor
      if (this.dateRange && this.dateRange.length > 1) {
        params['date_from'] = this.dateRange[0].toISODate()
        params['date_to'] = this.dateRange[this.dateRange.length - 1].toISODate()
      }
      this.auth.orders(params)
        .then(response => {
            this.orderHistoryList = response.data.data.items;
            this.vendorOptions = response.data.data.vendors;
            this.currentPage = response.data.data.page;
            this.limit = response.data.data.limit;
            this.totalCount = response.data.data.total_count;
            this.isLoading = false;
        })
    },
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    },
    formatDateRange(range) {
      if (!range || range.length < 2) return ''
      const start = new Date(range[0]).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      const end = new Date(range[range.length - 1]).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      return `${start} - ${end}`
    },
    getVendorName(vendorId) {
      const vendor = this.vendorOptions.find(v => v.id === vendorId)
      return vendor ? vendor.title : 'Unknown Vendor'
    },
    debounceSearch() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.applyFilters()
      }, 500)
    },
    applyFilters() {
      this.isLoading = true
      this.currentPage = 1
      this.loadUserHistory()
    },
    applyDateFilter() {
      if (this.dateRange.length <= 1) {
        return
      }
      this.dateMenu = false
      this.applyFilters()
    },
    clearSearch() {
      this.searchQuery = ""
      this.applyFilters()
    },
    clearVendorFilter() {
      this.selectedVendor = null
      this.applyFilters()
    },
    clearDateFilter() {
      this.dateRange = []
      this.dateMenu = false
      this.applyFilters()
    },
    clearAllFilters() {
      this.searchQuery = ""
      this.selectedVendor = null
      this.dateRange = []
      this.applyFilters()
    },
  }
}
</script>

<style lang="css" scoped>
.v-expansion-panel-title {
  padding: 12px 16px !important;
}

.v-expansion-panel-text {
  padding: 0 16px 16px !important;
}

.v-list-item {
  min-height: auto !important;
  padding: 8px 0 !important;
}

.text-caption {
  font-size: 12px !important;
}

</style>
