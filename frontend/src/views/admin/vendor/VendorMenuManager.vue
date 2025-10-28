<template>
  <v-container
    v-if="auth.isLoggedIn"
    fluid
    class="pa-2 pa-md-4"
  >
    <!-- Header -->
    <v-row class="mb-4">
      <v-col>
        <h1 class="text-h4 text-md-h3">
          Menü kezelés
        </h1>
      </v-col>
    </v-row>

    <!-- Create Menu Section -->
    <v-row class="mb-4">
      <v-col>
        <v-card
          elevation="2"
          class="pa-4"
        >
          <v-card-title class="text-h6 pa-0 mb-3">
            Új menü létrehozása
          </v-card-title>

          <v-row class="align-center">
            <v-col
              cols="12"
              md="6"
            >
              <v-text-field
                v-model="newMenu.name"
                label="Név"
                variant="outlined"
                density="compact"
                hide-details
              />
            </v-col>
            <v-col
              cols="12"
              md="6"
            >
              <div class="d-flex flex-wrap ga-2">
                <v-btn
                  color="primary"
                  variant="flat"
                  prepend-icon="mdi-plus"
                  @click="addMenu()"
                >
                  Létrehoz
                </v-btn>
                <v-btn
                  color="primary"
                  variant="outlined"
                  prepend-icon="mdi-import"
                  @click="openImportPopup()"
                >
                  Importálás
                </v-btn>
                <v-btn
                  v-if="selectedVendor.type === 'plugin'"
                  color="primary"
                  variant="outlined"
                  prepend-icon="mdi-qrcode-scan"
                  @click="openScanPopup()"
                >
                  Scan
                </v-btn>
              </div>
            </v-col>
          </v-row>
        </v-card>
      </v-col>
    </v-row>
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

          <!-- Active Filter -->
          <v-col
            cols="12"
            md="4"
          >
            <v-checkbox
              v-model="searchActive"
              label="Csak aktív menük"
              variant="outlined"
              density="compact"
              clearable
              color="primary"
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
              v-if="searchActive"
              closable
              color="primary"
              variant="outlined"
              @click:close="clearActive"
            >
              <v-icon
                small
                class="mr-1"
              >
                mdi-store
              </v-icon>
              {{ searchActive }}
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
    <!-- Mobile Cards View -->
    <v-row
      v-if="!isLoading && $vuetify.display.mobile"
      class="d-md-none"
    >
      <v-col cols="12">
        <v-card
          v-for="[id, menu] in menulist"
          :key="id"
          class="mb-3"
          elevation="2"
        >
          <v-card-text class="pb-2">
            <div class="d-flex justify-space-between align-center mb-2">
              <div class="text-subtitle-1 font-weight-bold">
                #{{ menu.id }}
              </div>
              <v-chip
                :color="menu.active ? 'success' : 'default'"
                size="small"
                variant="flat"
              >
                {{ menu.active ? 'Aktív' : 'Inaktív' }}
              </v-chip>
            </div>

            <div class="text-body-2 mb-2">
              <strong>Név:</strong>
              <v-text-field
                v-if="menu.isEditing"
                v-model="menu.name"
                variant="outlined"
                density="compact"
                hide-details
                class="mt-1"
              />
              <span v-else>{{ menu.name }}</span>
            </div>

            <div class="text-body-2 mb-2">
              <strong>Dátumtól:</strong>
              <v-text-field
                v-if="menu.isEditing"
                v-model="menu.from_date"
                variant="outlined"
                density="compact"
                hide-details
                type="date"
                class="mt-1"
              />
              <span v-else>{{ menu.from_date || '-' }}</span>
            </div>

            <div class="text-body-2 mb-3">
              <strong>Dátumig:</strong>
              <v-text-field
                v-if="menu.isEditing"
                v-model="menu.to_date"
                variant="outlined"
                density="compact"
                hide-details
                type="date"
                class="mt-1"
              />
              <span v-else>{{ menu.to_date || '-' }}</span>
            </div>
          </v-card-text>

          <v-card-actions class="pt-0">
            <!-- Normal state buttons -->
            <div
              v-if="!menu.isEditing"
              class="d-flex ga-2 flex-wrap"
            >
              <v-btn
                :color="menu.active ? 'warning' : 'success'"
                variant="text"
                size="small"
                :prepend-icon="menu.active ? 'mdi-toggle-switch' : 'mdi-toggle-switch-off'"
                @click="toggleActivation(menu)"
              >
                {{ menu.active ? 'Kikapcsol' : 'Bekapcsol' }}
              </v-btn>
              <v-btn
                color="primary"
                variant="text"
                size="small"
                prepend-icon="mdi-pencil"
                @click="edit(menu.id)"
              >
                Szerkesztés
              </v-btn>
              <v-btn
                color="info"
                variant="text"
                size="small"
                prepend-icon="mdi-eye"
                @click="openItemManager(menu.id)"
              >
                Termékek
              </v-btn>
              <v-btn
                color="secondary"
                variant="text"
                size="small"
                prepend-icon="mdi-content-copy"
                @click="duplicateMenu(menu.id)"
              >
                Duplikál
              </v-btn>
              <v-btn
                color="error"
                variant="text"
                size="small"
                prepend-icon="mdi-delete"
                @click="confirmDeleteMenu(menu)"
              >
                Törlés
              </v-btn>
            </div>

            <!-- Edit state buttons -->
            <div
              v-else
              class="d-flex ga-2"
            >
              <v-btn
                color="success"
                variant="text"
                size="small"
                prepend-icon="mdi-content-save"
                @click="updateMenu(menu.id)"
              >
                Mentés
              </v-btn>
              <v-btn
                color="grey"
                variant="text"
                size="small"
                prepend-icon="mdi-close"
                @click="cancelEdit(menu.id)"
              >
                Mégse
              </v-btn>
            </div>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- Desktop Table View -->
    <v-row
      class="d-none d-md-flex"
    >
      <v-col>
        <v-data-table
          :headers="headers"
          :items="Array.from(menulist.values())"
          :loading="isLoading"
          loading-text="Adatok betöltése"
          :items-per-page="limit"
          :items-per-page-options="itemsPerPageOptions"
          :items-length="totalCount"
          class="elevation-1"
          hover
          fixed-header
          @update:items-per-page="updateItemsPerPage"
          @update:page="handlePageChange"
        >
          <!-- ID column -->
          <template #item.id="{ item }">
            <span class="font-weight-bold">#{{ item.id }}</span>
          </template>

          <!-- Name column -->
          <template #item.name="{ item }">
            <v-text-field
              v-if="item.isEditing"
              v-model="item.name"
              variant="outlined"
              density="compact"
              hide-details
            />
            <span v-else>{{ item.name }}</span>
          </template>

          <!-- From date column -->
          <template #item.from_date="{ item }">
            <v-text-field
              v-if="item.isEditing"
              v-model="item.from_date"
              variant="outlined"
              density="compact"
              hide-details
              type="date"
              style="width: 160px;"
            />
            <span v-else>{{ item.from_date || '-' }}</span>
          </template>

          <!-- To date column -->
          <template #item.to_date="{ item }">
            <v-text-field
              v-if="item.isEditing"
              v-model="item.to_date"
              variant="outlined"
              density="compact"
              hide-details
              type="date"
              style="width: 160px;"
            />
            <span v-else>{{ item.to_date || '-' }}</span>
          </template>

          <!-- Active column -->
          <template #item.active="{ item }">
            <v-chip
              :color="item.active ? 'success' : 'default'"
              size="small"
              variant="flat"
            >
              {{ item.active ? 'Aktív' : 'Inaktív' }}
            </v-chip>
          </template>

          <!-- Actions column -->
          <template #item.actions="{ item }">
            <div
              v-if="!item.isEditing"
              class="d-flex ga-1"
            >
              <v-tooltip text="Aktiválás ki/be">
                <template #activator="{ props }">
                  <v-btn
                    v-bind="props"
                    :icon="item.active ? 'mdi-toggle-switch' : 'mdi-toggle-switch-off'"
                    :color="item.active ? 'warning' : 'success'"
                    variant="text"
                    size="small"
                    @click="toggleActivation(item)"
                  />
                </template>
              </v-tooltip>

              <v-tooltip text="Szerkesztés">
                <template #activator="{ props }">
                  <v-btn
                    v-bind="props"
                    icon="mdi-pencil"
                    color="primary"
                    variant="text"
                    size="small"
                    @click="edit(item.id)"
                  />
                </template>
              </v-tooltip>

              <v-tooltip text="Termékek kezelése">
                <template #activator="{ props }">
                  <v-btn
                    v-bind="props"
                    icon="mdi-eye"
                    color="info"
                    variant="text"
                    size="small"
                    @click="openItemManager(item.id)"
                  />
                </template>
              </v-tooltip>

              <v-tooltip text="Duplikálás">
                <template #activator="{ props }">
                  <v-btn
                    v-bind="props"
                    icon="mdi-content-copy"
                    color="secondary"
                    variant="text"
                    size="small"
                    @click="duplicateMenu(item.id)"
                  />
                </template>
              </v-tooltip>

              <v-tooltip text="Törlés">
                <template #activator="{ props }">
                  <v-btn
                    v-bind="props"
                    icon="mdi-delete"
                    color="error"
                    variant="text"
                    size="small"
                    @click="confirmDeleteMenu(item)"
                  />
                </template>
              </v-tooltip>
            </div>

            <div
              v-else
              class="d-flex ga-1"
            >
              <v-tooltip text="Mentés">
                <template #activator="{ props }">
                  <v-btn
                    v-bind="props"
                    icon="mdi-content-save"
                    color="success"
                    variant="text"
                    size="small"
                    @click="updateMenu(item.id)"
                  />
                </template>
              </v-tooltip>

              <v-tooltip text="Mégse">
                <template #activator="{ props }">
                  <v-btn
                    v-bind="props"
                    icon="mdi-close"
                    color="grey"
                    variant="text"
                    size="small"
                    @click="cancelEdit(item.id)"
                  />
                </template>
              </v-tooltip>
            </div>
          </template>

          <!-- Custom bottom pagination -->
          <template #bottom>
            <div class="d-flex justify-space-between align-center pa-4">
              <div class="text-body-2 text-medium-emphasis">
                {{ paginationText }}
              </div>
              <div class="d-flex align-center ga-4">
                <v-select
                  v-model="limit"
                  :items="itemsPerPageOptions"
                  label="Elemek száma"
                  variant="outlined"
                  density="compact"
                  hide-details
                  style="min-width: 120px;"
                />
                <v-pagination
                  v-model="currentPage"
                  :length="Math.ceil(totalCount / limit)"
                  :total-visible="$vuetify.display.mobile ? 5 : 7"
                  size="small"
                />
              </div>
            </div>
          </template>
        </v-data-table>
      </v-col>
    </v-row>

    <!-- Mobile Pagination -->
    <v-row
      v-if="!isLoading && $vuetify.display.mobile"
      class="d-md-none"
    >
      <v-col class="d-flex flex-column align-center ga-4">
        <div class="text-body-2 text-medium-emphasis">
          {{ paginationText }}
        </div>
        <div class="d-flex align-center ga-4">
          <v-select
            v-model="limit"
            :items="itemsPerPageOptions"
            label="Elemek/oldal"
            variant="outlined"
            density="compact"
            hide-details
            style="min-width: 120px;"
          />
          <v-pagination
            v-model="currentPage"
            :length="Math.ceil(totalCount / limit)"
            :total-visible="5"
            size="small"
          />
        </div>
      </v-col>
    </v-row>

    <!-- Loading state -->
    <v-row v-if="isLoading">
      <v-col class="text-center py-12">
        <v-progress-circular
          indeterminate
          size="64"
          color="primary"
        />
        <div class="text-h6 mt-4">
          Menük betöltése...
        </div>
      </v-col>
    </v-row>

    <!-- Import Dialog -->
    <v-dialog
      v-model="showImportPopup"
      max-width="600"
      :fullscreen="$vuetify.display.mobile"
      :transition="$vuetify.display.mobile ? 'dialog-bottom-transition' : 'dialog-transition'"
    >
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon
            class="me-2"
            color="primary"
          >
            mdi-import
          </v-icon>
          <span class="text-h6">Menü importálása JSON fájlból</span>
          <v-spacer />
          <v-btn
            v-if="$vuetify.display.mobile"
            icon="mdi-close"
            variant="text"
            @click="showImportPopup = false"
          />
        </v-card-title>

        <v-card-text class="py-4">
          <v-alert
            type="info"
            class="mb-4"
          >
            A JSON fájlnak követnie kell egy meghatározott struktúrát. Bővebben lásd a dokumentációban.
          </v-alert>

          <v-file-input
            v-model="uploadedFiles"
            label="JSON fájl"
            accept=".json"
            variant="outlined"
            prepend-icon="mdi-file-document"
            @change="handleFileUpload"
          />
        </v-card-text>

        <v-card-actions class="pa-4">
          <v-spacer v-if="!$vuetify.display.mobile" />
          <v-btn
            :block="$vuetify.display.mobile"
            color="grey-darken-1"
            variant="outlined"
            class="mb-2 mb-sm-0"
            @click="showImportPopup = false"
          >
            Mégse
          </v-btn>
          <v-btn
            :block="$vuetify.display.mobile"
            color="primary"
            variant="flat"
            :disabled="!file"
            @click="submitJsonFile()"
          >
            Importálás
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Scan Dialog -->
    <v-dialog
      v-model="showScanPopup"
      max-width="400"
      :fullscreen="$vuetify.display.mobile"
      :transition="$vuetify.display.mobile ? 'dialog-bottom-transition' : 'dialog-transition'"
    >
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon
            class="me-2"
            color="primary"
          >
            mdi-qrcode-scan
          </v-icon>
          <span class="text-h6">Menü scan indítás</span>
          <v-spacer />
          <v-btn
            v-if="$vuetify.display.mobile"
            icon="mdi-close"
            variant="text"
            @click="showScanPopup = false"
          />
        </v-card-title>

        <v-card-text class="py-4">
          <div class="text-body-1 mb-4">
            Válaszd ki a megfelelő dátumot
          </div>
          <v-date-picker
            v-model="scanDate"
            show-adjacent-months
            first-day-of-week="1"
            hide-header
            full-width
          />
        </v-card-text>

        <v-card-actions class="pa-4">
          <v-spacer v-if="!$vuetify.display.mobile" />
          <v-btn
            :block="$vuetify.display.mobile"
            color="grey-darken-1"
            variant="outlined"
            class="mb-2 mb-sm-0"
            @click="showScanPopup = false"
          >
            Mégse
          </v-btn>
          <v-btn
            :block="$vuetify.display.mobile"
            color="primary"
            variant="flat"
            @click="submitScan()"
          >
            Scan
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete confirmation dialog -->
    <v-dialog
      v-model="deleteDialog"
      max-width="500"
      :fullscreen="$vuetify.display.mobile"
      :transition="$vuetify.display.mobile ? 'dialog-bottom-transition' : 'dialog-transition'"
    >
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon
            class="me-2"
            color="primary"
          >
            mdi-delete-alert
          </v-icon>
          <span class="text-h6">Menü törlése</span>
          <v-spacer />
          <v-btn
            v-if="$vuetify.display.mobile"
            icon="mdi-close"
            variant="text"
            @click="deleteDialog = false"
          />
        </v-card-title>

        <v-card-text class="py-4">
          <div class="text-body-1 mb-4">
            Biztosan törölni szeretnéd a
            <strong class="text-error">#{{ selectedMenu?.id }}</strong>
            számú menüt?
          </div>
          <v-alert
            type="warning"
            class="mb-4"
          >
            Ez a művelet nem visszavonható!
          </v-alert>
          <div class="text-body-2">
            <strong>Név:</strong> {{ selectedMenu?.name }}
          </div>
        </v-card-text>

        <v-card-actions class="pa-4">
          <v-spacer v-if="!$vuetify.display.mobile" />
          <v-btn
            :block="$vuetify.display.mobile"
            color="grey-darken-1"
            variant="outlined"
            class="mb-2 mb-sm-0"
            @click="deleteDialog = false"
          >
            Mégse
          </v-btn>
          <v-btn
            :block="$vuetify.display.mobile"
            color="primary"
            variant="flat"
            @click="deleteMenu"
          >
            Törlés
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Snackbar -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="4000"
      :location="$vuetify.display.mobile ? 'top' : 'bottom end'"
      :multi-line="$vuetify.display.mobile"
    >
      {{ snackbar.text }}
      <template #actions>
        <v-btn
          color="white"
          variant="text"
          @click="snackbar.show = false"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from "@/stores/auth"
import { useMenuStore } from "@/stores/menu"
import { useVendorStore } from "@/stores/vendor"

// Composables
const route = useRoute()
const router = useRouter()
const auth = useAuth()
const menuStore = useMenuStore()
const vendorStore = useVendorStore()

// Reactive data
const menulist = ref(new Map())
const newMenu = ref({ name: "" })
const isLoading = ref(true)
const showImportPopup = ref(false)
const showScanPopup = ref(false)
const scanDate = ref(new Date())

const searchQuery = ref("")
const searchActive = ref(true)
const dateMenu = ref(false)
const dateRange = ref([])
const searchTimeout = ref(null)

const uploadedFiles = ref([])
const file = ref(null)
const limit = ref(10)
const currentPage = ref(1)
const totalCount = ref(0)
const deleteDialog = ref(false)
const selectedMenu = ref(null)
const snackbar = ref({
  show: false,
  text: '',
  color: 'success'
})

// Items per page options
const itemsPerPageOptions = [
  { value: 5, title: '5' },
  { value: 10, title: '10' },
  { value: 25, title: '25' },
  { value: 50, title: '50' }
]

// Table headers configuration
const headers = [
  {
    title: '#',
    key: 'id',
    align: 'start',
    sortable: false,
    width: '80px'
  },
  {
    title: 'Név',
    key: 'name',
    align: 'start',
    sortable: false,
    minWidth: '200px'
  },
  {
    title: 'Dátumtól',
    key: 'from_date',
    align: 'start',
    sortable: false,
    width: '180px'
  },
  {
    title: 'Dátumig',
    key: 'to_date',
    align: 'start',
    sortable: false,
    width: '180px'
  },
  {
    title: 'Aktív',
    key: 'active',
    align: 'center',
    sortable: false,
    width: '100px'
  },
  {
    title: 'Műveletek',
    key: 'actions',
    align: 'center',
    sortable: false,
    width: '280px'
  }
]

// Computed properties
const selectedVendor = computed(() => {
  return vendorStore.selectedVendor || { type: '' }
})

const paginationText = computed(() => {
  const start = (currentPage.value - 1) * limit.value + 1
  const end = Math.min(currentPage.value * limit.value, totalCount.value)
  return `${start}-${end} / ${totalCount.value}`
})

const hasActiveFilters = computed(() => {
  return searchQuery.value || searchActive.value || (dateRange.value && dateRange.value.length > 1)
})


// Watchers
watch([currentPage, limit], () => {
  loadMenu()
})

// Methods

const loadMenu  = () => {
  let params = {
      "limit": limit.value,
      "page": currentPage.value
    }
  if (searchQuery.value) params['search'] = searchQuery.value
  if (searchActive.value) params['active'] = searchActive.value
  if (dateRange.value && dateRange.value.length > 1) {
    params['date_from'] = dateRange.value[0].toISODate()
    params['date_to'] = dateRange.value[dateRange.value.length - 1].toISODate()
  }

  vendorStore.fetchMenus(route.params.id, params).then(response => {
    const newMenuList = new Map(
      response.data.data.menus.map(
        item => [item.id, { ...item, isEditing: false }]
      )
    )

    currentPage.value = response.data.data.page
    limit.value = response.data.data.limit
    totalCount.value = response.data.data.total_count
    menulist.value = newMenuList
    isLoading.value = false
  })
}

const handlePageChange = (page) => {
  isLoading.value = true
  currentPage.value = page;
  loadMenu()
}

const formatDateRange = (range) => {
  if (!range || range.length < 2) return ''
  const start = new Date(range[0]).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  const end = new Date(range[range.length - 1]).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  return `${start} - ${end}`
}

const debounceSearch = () => {
  clearTimeout(searchTimeout.value)
  searchTimeout.value = setTimeout(() => {
    applyFilters()
  }, 500)
}

const applyFilters = () => {
  isLoading.value = true
  currentPage.value = 1
  loadMenu()
}

const applyDateFilter = () => {
  if (dateRange.value.length <= 1) {
    return
  }
  dateMenu.value = false
  applyFilters()
}

const clearSearch = () => {
  searchQuery.value = ""
  applyFilters()
}

const clearActive = () => {
  searchActive.value = false
  applyFilters()
}

const clearDateFilter = () => {
  dateRange.value = []
  dateMenu.value = false
  applyFilters()
}

const clearAllFilters = () => {
  searchQuery.value = ""
  searchActive.value = true
  dateRange.value = []
  applyFilters()
}

const updateItemsPerPage = (newItemsPerPage) => {
  limit.value = newItemsPerPage
  currentPage.value = 1
}

const openImportPopup = () => {
  showImportPopup.value = true
}

const openScanPopup = () => {
  showScanPopup.value = true
}

const submitJsonFile = async () => {
  try {
    const formData = new FormData()
    formData.append("file", file.value)
    const response = await vendorStore.import(route.params.id, formData)

    if (response.status === 201) {
      showImportPopup.value = false
      loadMenu()
    }
  } catch (error) {
    console.error('Error importing menu:', error)
  }
}

const submitScan = async () => {
  try {
    const response = await vendorStore.scan(route.params.id, scanDate.value.toISOString().split('T')[0])

    if (response.status === 201) {
      showScanPopup.value = false
      loadMenu()
    }
  } catch (error) {
    console.error('Error scanning menu:', error)
  }
}

const handleFileUpload = (event) => {
  const selectedFile = event.target.files?.[0] || uploadedFiles.value?.[0]

  if (selectedFile && selectedFile.type === "application/json") {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const json = JSON.parse(e.target.result)
        console.log("Valid JSON:", json)
        file.value = selectedFile
      } catch (error) {
        console.log("Invalid JSON:", error)
      }
    }
    reader.readAsText(selectedFile)
  }
}

const toggleActivation = async (menu) => {
  try {
    let result
    if (menu.active) {
      result = await menuStore.deactivate(menu.id)
    } else {
      result = await menuStore.activate(menu.id)
    }

    if (result.status === 200) {
      loadMenu()
    }
  } catch (error) {
    console.error('Error toggling activation:', error)
  }
}

const addMenu = async () => {
  try {
    const menuData = {
      ...newMenu.value,
      vendor_id: route.params.id
    }
    const response = await menuStore.add(menuData)

    if (response.status === 201) {
      newMenu.value = { name: "" }
      loadMenu()
    }
  } catch (error) {
    console.error('Error adding menu:', error)
  }
}

const edit = (menuId) => {
  const menu = menulist.value.get(menuId)
  if (menu) {
    menulist.value.set(menuId, { ...menu, isEditing: true })
  }
}

const cancelEdit = (menuId) => {
  const menu = menulist.value.get(menuId)
  if (menu) {
    menulist.value.set(menuId, { ...menu, isEditing: false })
  }
}

const updateMenu = async (menuId) => {
  try {
    const menu = menulist.value.get(menuId)
    if (!menu) return

    const updateData = { ...menu }

    if (!updateData.from_date) {
      delete updateData["from_date"]
    }
    if (!updateData.to_date) {
      delete updateData["to_date"]
    }

    delete updateData["isEditing"]

    const response = await menuStore.update(menuId, updateData)

    if (response.status === 200) {
      loadMenu()
    }
  } catch (error) {
    console.error('Error updating menu:', error)
  }
}

const confirmDeleteMenu = (menu) => {
  selectedMenu.value = menu
  deleteDialog.value = true
}

const deleteMenu = async () => {
  try {
    if (!selectedMenu.value) return

    const response = await menuStore.delete(selectedMenu.value.id)

    if (response.status === 200) {
      deleteDialog.value = false
      selectedMenu.value = null
      loadMenu()
    }
  } catch (error) {
    console.error('Error deleting menu:', error)
  }
}

const duplicateMenu = async (menuId) => {
  try {
    const menu = menulist.value.get(menuId)
    if (!menu) return

    const duplicateData = { ...menu }
    delete duplicateData["isEditing"]

    const response = await menuStore.duplicate(menuId, duplicateData)

    if (response.status === 200) {
      loadMenu()
    }
  } catch (error) {
    console.error('Error duplicating menu:', error)
  }
}

const openItemManager = (menuId) => {
  router.push({ path: `/admin/${route.params.id}/menu/${menuId}` })
}

// Lifecycle
onMounted(() => {
  loadMenu()
})
</script>
