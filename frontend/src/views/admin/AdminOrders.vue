<template>
  <v-container
    v-if="auth.isLoggedIn"
    fluid
    class="pa-2 pa-md-4"
  >
    <!-- Header -->
    <v-row class="mb-4">
      <v-col>
        <h1 class="text-h5 text-md-h4">
          Rendelések
        </h1>
      </v-col>
    </v-row>

    <!-- Mobile Cards View -->
    <v-row
      v-if="!isLoading && $vuetify.display.mobile"
      class="d-md-none"
    >
      <v-col cols="12">
        <v-card
          v-for="order in orders"
          :key="order.id"
          class="mb-3"
          elevation="2"
        >
          <v-card-text class="pb-2">
            <div class="d-flex justify-space-between align-center mb-2">
              <div class="text-subtitle-1 font-weight-bold">
                #{{ order.id }}
              </div>
              <v-chip
                :color="getStatusColor(order.state_id)"
                size="small"
                variant="flat"
              >
                {{ order.state_id }}
              </v-chip>
            </div>

            <div class="text-body-2 mb-2">
              <strong>Üzlet:</strong> {{ order.vendor }}
            </div>
            <div class="text-body-2 mb-2">
              <strong>Felhasználó:</strong> {{ order.user_id }}
            </div>
            <div class="text-body-2 mb-2">
              <strong>Dátum:</strong> {{ formatDate(order.date_of_order) }}
            </div>
            <div class="text-body-2 mb-3">
              <strong>Díj:</strong>
              <v-text-field
                v-if="editing === order.id"
                v-model.number="order.order_fee"
                type="number"
                step="50"
                variant="outlined"
                density="compact"
                hide-details
                suffix="Ft"
                class="d-inline-block"
                style="width: 120px; vertical-align: middle;"
              />
              <span v-else>{{ order.order_fee }} Ft</span>
            </div>

            <!-- Mobile Status Edit -->
            <div
              v-if="editing === order.id"
              class="mb-3"
            >
              <v-select
                v-model="order.state_id"
                :items="orderStates"
                label="Állapot"
                variant="outlined"
                density="compact"
                hide-details
              >
                <template #selection="{ item }">
                  <v-chip
                    :color="getStatusColor(item.value)"
                    size="small"
                    variant="flat"
                  >
                    {{ item.title }}
                  </v-chip>
                </template>
                <template #item="{ props, item }">
                  <v-list-item
                    v-bind="props"
                    title=""
                  >
                    <v-chip
                      :color="getStatusColor(item.value)"
                      size="small"
                      variant="flat"
                    >
                      {{ item.title }}
                    </v-chip>
                  </v-list-item>
                </template>
              </v-select>
            </div>
          </v-card-text>

          <v-card-actions class="pt-0">
            <!-- Normal state buttons -->
            <div
              v-if="editing !== order.id"
              class="d-flex ga-2 flex-wrap"
            >
              <v-btn
                color="primary"
                variant="text"
                size="small"
                prepend-icon="mdi-pencil"
                @click="editOrder(order.id)"
              >
                Szerkesztés
              </v-btn>
              <v-btn
                color="info"
                variant="text"
                size="small"
                prepend-icon="mdi-eye"
                @click="viewOrder(order)"
              >
                Részletek
              </v-btn>
              <v-btn
                v-if="canDeleteOrder(order)"
                color="error"
                variant="text"
                size="small"
                prepend-icon="mdi-delete"
                @click="confirmDeleteOrder(order)"
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
                @click="updateOrder(order)"
              >
                Mentés
              </v-btn>
              <v-btn
                color="grey"
                variant="text"
                size="small"
                prepend-icon="mdi-close"
                @click="cancelEdit()"
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
      v-if="!isLoading"
      class="d-none d-md-flex"
    >
      <v-col>
        <v-data-table
          :headers="headers"
          :items="orders"
          :loading="isLoading"
          :items-per-page="itemsPerPage"
          :items-per-page-options="itemsPerPageOptions"
          :items-length="totalItems"
          class="elevation-1"
          hover
          fixed-header
          @update:items-per-page="updateItemsPerPage"
          @update:page="updatePage"
        >
          <!-- Order ID column -->
          <template #item.id="{ item }">
            <span class="font-weight-bold">#{{ item.id }}</span>
          </template>

          <!-- Status column -->
          <template #item.state_id="{ item }">
            <v-select
              v-if="editing === item.id"
              v-model="item.state_id"
              :items="orderStates"
              variant="outlined"
              density="compact"
              hide-details
            >
              <template #selection="{ item: selectItem }">
                <v-chip
                  :color="getStatusColor(selectItem.value)"
                  size="small"
                  variant="flat"
                >
                  {{ selectItem.title }}
                </v-chip>
              </template>
              <template #item="{ props, item: selectItem }">
                <v-list-item
                  v-bind="props"
                  title=""
                >
                  <v-chip
                    :color="getStatusColor(selectItem.value)"
                    size="small"
                    variant="flat"
                  >
                    {{ selectItem.title }}
                  </v-chip>
                </v-list-item>
              </template>
            </v-select>
            <v-chip
              v-else
              :color="getStatusColor(item.state_id)"
              size="small"
              variant="flat"
            >
              {{ item.state_id }}
            </v-chip>
          </template>

          <!-- Date column -->
          <template #item.date_of_order="{ item }">
            {{ formatDate(item.date_of_order) }}
          </template>

          <!-- Order fee column -->
          <template #item.order_fee="{ item }">
            <v-text-field
              v-if="editing === item.id"
              v-model.number="item.order_fee"
              type="number"
              step="50"
              variant="outlined"
              density="compact"
              hide-details
              suffix="Ft"
              style="width: 120px;"
            />
            <span v-else>{{ item.order_fee }} Ft</span>
          </template>

          <!-- Actions column -->
          <template #item.actions="{ item }">
            <div
              v-if="editing !== item.id"
              class="d-flex ga-2"
            >
              <v-tooltip text="Szerkesztés">
                <template #activator="{ props }">
                  <v-btn
                    v-bind="props"
                    icon="mdi-pencil"
                    color="primary"
                    variant="text"
                    size="small"
                    @click="editOrder(item.id)"
                  />
                </template>
              </v-tooltip>

              <v-tooltip text="Rendelés részletei">
                <template #activator="{ props }">
                  <v-btn
                    v-bind="props"
                    icon="mdi-eye"
                    color="primary"
                    variant="text"
                    size="small"
                    @click="viewOrder(item)"
                  />
                </template>
              </v-tooltip>

              <v-tooltip
                v-if="canDeleteOrder(item)"
                text="Rendelés törlése"
              >
                <template #activator="{ props }">
                  <v-btn
                    v-bind="props"
                    icon="mdi-delete"
                    color="primary"
                    variant="text"
                    size="small"
                    @click="confirmDeleteOrder(item)"
                  />
                </template>
              </v-tooltip>
            </div>

            <div
              v-else
              class="d-flex ga-2"
            >
              <v-tooltip text="Mentés">
                <template #activator="{ props }">
                  <v-btn
                    v-bind="props"
                    icon="mdi-content-save"
                    color="primary"
                    variant="text"
                    size="small"
                    @click="updateOrder(item)"
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
                    @click="cancelEdit()"
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
                  v-model="itemsPerPage"
                  :items="itemsPerPageOptions"
                  label="Elemek száma"
                  variant="outlined"
                  density="compact"
                  hide-details
                  style="min-width: 120px;"
                />
                <v-pagination
                  v-model="page"
                  :length="Math.ceil(totalItems / itemsPerPage)"
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
            v-model="itemsPerPage"
            :items="itemsPerPageOptions"
            label="Elemek/oldal"
            variant="outlined"
            density="compact"
            hide-details
            style="min-width: 120px;"
          />
          <v-pagination
            v-model="page"
            :length="Math.ceil(totalItems / itemsPerPage)"
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
          Rendelések betöltése...
        </div>
      </v-col>
    </v-row>

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
          <span class="text-h6">Rendelés törlése</span>
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
            <strong class="text-error">#{{ selectedOrder?.id }}</strong>
            számú rendelést?
          </div>
          <v-alert
            type="secondary"
            class="mb-4"
          >
            Ez a művelet nem visszavonható!
          </v-alert>
          <div class="text-body-2">
            <strong>Üzlet:</strong> {{ selectedOrder?.vendor }}<br>
            <strong>Felhasználó:</strong> {{ selectedOrder?.user_id }}<br>
            <strong>Dátum:</strong> {{ formatDate(selectedOrder?.date_of_order) }}
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
            @click="deleteOrder"
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
import { useAuth } from "@/stores/auth"
import { useOrderStore } from "@/stores/order"

// Composables
const auth = useAuth()
const orderStore = useOrderStore()

// Reactive data
const orders = ref([])
const isLoading = ref(true)
const page = ref(1)
const itemsPerPage = ref(10)
const totalItems = ref(0)
const editing = ref(false)
const editOriginal = ref(null)
const deleteDialog = ref(false)
const selectedOrder = ref(null)
const snackbar = ref({
  show: false,
  text: '',
  color: 'success'
})

// Order states
const orderStates = ["collect", "order", "closed"]

// Items per page options
const itemsPerPageOptions = [
  { value: 5, title: '5' },
  { value: 10, title: '10' },
  { value: 25, title: '25' },
  { value: 50, title: '50' },
  { value: -1, title: 'Összes' }
]

// Table headers configuration
const headers = [
  {
    title: '#',
    key: 'id',
    align: 'start',
    sortable: true,
    width: '80px'
  },
  {
    title: 'Üzlet',
    key: 'vendor',
    align: 'start',
    sortable: true,
    minWidth: '150px'
  },
  {
    title: 'Állapot',
    key: 'state_id',
    align: 'center',
    sortable: true,
    width: '140px'
  },
  {
    title: 'Felhasználó',
    key: 'user_id',
    align: 'start',
    sortable: true,
    minWidth: '120px'
  },
  {
    title: 'Dátum',
    key: 'date_of_order',
    align: 'start',
    sortable: true,
    width: '120px'
  },
  {
    title: 'Rendelési díj',
    key: 'order_fee',
    align: 'end',
    sortable: true,
    width: '140px'
  },
  {
    title: 'Műveletek',
    key: 'actions',
    align: 'center',
    sortable: false,
    width: '200px'
  }
]

// Computed properties
const paginationText = computed(() => {
  const start = (page.value - 1) * itemsPerPage.value + 1
  const end = Math.min(page.value * itemsPerPage.value, totalItems.value)
  return `${start}-${end} / ${totalItems.value}`
})

// Watchers
watch([page, itemsPerPage], () => {
  if (editing.value) {
    cancelEdit()
  }
  refreshOrdersList()
})

// Methods
const updatePage = (newPage) => {
  page.value = newPage
}

const updateItemsPerPage = (newItemsPerPage) => {
  itemsPerPage.value = newItemsPerPage
  page.value = 1
}

const refreshOrdersList = async () => {
  try {
    isLoading.value = true
    const response = await orderStore.fetchAll({
      limit: itemsPerPage.value === -1 ? 1000 : itemsPerPage.value,
      page: page.value
    })

    if (response.status === 200) {
      orders.value = response.data.data.items
      totalItems.value = response.data.data.total_count

      if (response.data.data.page !== page.value) {
        page.value = response.data.data.page
      }
    }
  } catch (error) {
    showSnackbar('Hiba történt a rendelések betöltése során', 'error')
    console.error('Error fetching orders:', error)
  } finally {
    isLoading.value = false
  }
}

const editOrder = (orderId) => {
  const order = orders.value.find(o => o.id === orderId)
  if (order) {
    editOriginal.value = { ...order }
    editing.value = orderId
  }
}

const cancelEdit = () => {
  if (editOriginal.value) {
    const orderIndex = orders.value.findIndex(o => o.id === editing.value)
    if (orderIndex !== -1) {
      orders.value[orderIndex] = { ...editOriginal.value }
    }
  }
  editing.value = false
  editOriginal.value = null
}

const updateOrder = async (order) => {
  try {
    const response = await orderStore.update(order.id, {
      state_id: order.state_id,
      order_fee: order.order_fee
    })

    if (response.status === 200) {
      editing.value = false
      editOriginal.value = null
      showSnackbar('Rendelés sikeresen frissítve', 'success')
      refreshOrdersList()
    }
  } catch (error) {
    showSnackbar('Hiba történt a rendelés frissítése során', 'error')
    console.error('Error updating order:', error)
  }
}

const viewOrder = (order) => {
  // TODO: Implement order details view
  console.log('View order details:', order.id)
  showSnackbar(`#${order.id} rendelés részleteinek megtekintése - még nem implementált`, 'info')
}

const canDeleteOrder = (order) => {
  if (order.state_id === 'closed') {
    return false
  }

  const isEmpty = order.item_count === 0
  const oneWeekAgo = new Date()
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)
  const isOld = new Date(order.date_of_order) < oneWeekAgo

  return isEmpty || isOld
}

const confirmDeleteOrder = (order) => {
  selectedOrder.value = order
  deleteDialog.value = true
}

const deleteOrder = async () => {
  try {
    const response = await orderStore.delete(selectedOrder.value.id)
    if (response.status === 200) {
      showSnackbar(`#${selectedOrder.value.id} rendelés sikeresen törölve`, 'success')
      deleteDialog.value = false
      selectedOrder.value = null
      refreshOrdersList()
    } else {
      showSnackbar('Hiba történt a rendelés törlése során', 'error')
    }
  } catch (error) {
    showSnackbar('Hiba történt a rendelés törlése során', 'error')
    console.error('Error deleting order:', error)
  }
}

const getStatusColor = (status) => {
  switch (status) {
    case 'collect': return 'success'
    case 'order': return 'warning'
    case 'closed': return 'error'
    default: return 'default'
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('hu-HU', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

const showSnackbar = (text, color = 'success') => {
  snackbar.value = {
    show: true,
    text,
    color
  }
}

// Lifecycle
onMounted(() => {
  refreshOrdersList()
})
</script>

<style scoped>
/* Using Vuetify's built-in spacing classes */
</style>
