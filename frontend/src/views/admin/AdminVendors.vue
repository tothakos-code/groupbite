<template>
  <v-container
    fluid
    class="pa-2 pa-md-4"
  >
    <!-- Header with Actions -->
    <v-row class="d-none d-sm-flex mb-4">
      <v-col
        cols="6"
        md="8"
        class="d-flex align-center"
      >
        <h1 class="text-h4 text-md-h4">
          Üzlet kezelő
        </h1>
      </v-col>
      <v-col
        cols="6"
        md="4"
        class="d-flex justify-end ga-2"
      >
        <v-tooltip text="Lista frissítése">
          <template #activator="{ props }">
            <v-btn
              v-bind="props"
              icon="mdi-refresh"
              color="primary"
              variant="elevated"
              size="small"
              :loading="isLoading"
              @click="refreshVendorList"
            />
          </template>
        </v-tooltip>

        <v-tooltip text="Új üzlet hozzáadása">
          <template #activator="{ props }">
            <v-btn
              v-bind="props"
              icon="mdi-store-plus"
              color="primary"
              variant="elevated"
              size="small"
              @click="addVendor"
            />
          </template>
        </v-tooltip>
      </v-col>
    </v-row>

    <!-- Mobile Actions (visible only on mobile) -->
    <v-row class="d-flex d-sm-none mb-4">
      <v-col
        cols="6"
        class="d-flex ga-2"
      >
        <v-btn
          color="primary"
          variant="elevated"
          prepend-icon="mdi-refresh"
          block
          :loading="isLoading"
          @click="refreshVendorList"
        >
          Frissítés
        </v-btn>
        <v-btn
          color="primary"
          variant="elevated"
          prepend-icon="mdi-store-plus"
          block
          @click="addVendor"
        >
          Új üzlet
        </v-btn>
      </v-col>
    </v-row>

    <!-- Mobile Cards View -->
    <v-row
      v-if="!isLoading"
      class="d-flex d-sm-none"
    >
      <v-col cols="12">
        <v-card
          v-for="(vendor, index) in allVendorList"
          :key="vendor.id"
          class="mb-3"
          elevation="2"
          style="cursor: pointer"
          @click="openVendorConfiguration(vendor.id)"
        >
          <v-card-text class="pb-2">
            <div class="d-flex justify-space-between align-center mb-2">
              <div class="text-subtitle-1 font-weight-medium">
                #{{ index + 1 }} - {{ vendor.name }}
              </div>
              <v-chip
                :color="vendor.active ? 'primary' : ''"
                size="default"
                variant="flat"
              >
                {{ vendor.active ? 'Aktív' : 'Inaktív' }}
              </v-chip>
            </div>
            <div class="d-flex ga-2">
              <v-chip
                size="x-small"
                variant="tonal"
                :color="vendor.plugin_id ? 'deep-purple' : 'blue-grey'"
              >
                {{ vendor.plugin_id ? 'Plugin' : 'Beépített' }}
              </v-chip>
              <span
                v-if="vendor.plugin_id"
                class="text-caption text-medium-emphasis align-self-center"
              >{{ vendor.plugin_id }}</span>
            </div>
          </v-card-text>

          <v-card-actions class="pt-0">
            <v-btn
              color="primary"
              :prepend-icon="vendor.active ? 'mdi-toggle-switch' : 'mdi-toggle-switch-off'"
              variant="text"
              :loading="toggleLoading === vendor.id"
              @click.stop="toggleActivation(vendor)"
            >
              {{ vendor.active ? 'Deaktiválás' : 'Aktiválás' }}
            </v-btn>
            <v-spacer />
            <v-icon color="grey">mdi-chevron-right</v-icon>
          </v-card-actions>
        </v-card>

        <!-- Empty State for Mobile -->
        <v-card
          v-if="allVendorList.length === 0"
          class="text-center pa-8"
        >
          <v-icon
            size="64"
            color="grey-lighten-2"
            class="mb-4"
          >
            mdi-store-off
          </v-icon>
          <div class="text-h6 text-medium-emphasis mb-2">
            Nincs üzlet
          </div>
          <div class="text-body-2 text-medium-emphasis mb-4">
            Még nem található üzlet a rendszerben
          </div>
          <v-btn
            color="primary"
            variant="elevated"
            prepend-icon="mdi-store-plus"
            @click="addVendor"
          >
            Első üzlet hozzáadása
          </v-btn>
        </v-card>
      </v-col>
    </v-row>

    <!-- Desktop Table View -->
    <v-row
      v-if="!isLoading"
      class="d-none d-sm-flex"
    >
      <v-col>
        <v-data-table
          :headers="headers"
          :items="allVendorList"
          :loading="isLoading"
          class="elevation-1 vendor-table"
          hover
          no-data-text="Nincs üzlet a rendszerben"
          loading-text="Üzletek betöltése..."
          @click:row="(_, row) => openVendorConfiguration(row.item.id)"
        >
          <!-- Index column -->
          <template #item.index="{ index }">
            <span class="font-weight-bold">#{{ index + 1 }}</span>
          </template>

          <!-- Name column -->
          <template #item.name="{ item }">
            <div class="text-subtitle-2 font-weight-medium">
              {{ item.name }}
            </div>
          </template>

          <!-- Type column -->
          <template #item.menu_type="{ item }">
            <v-chip
              size="small"
              variant="tonal"
              :color="item.plugin_id ? 'deep-purple' : 'blue-grey'"
            >
              {{ item.plugin_id ? 'Plugin' : 'Beépített' }}
            </v-chip>
          </template>

          <!-- Plugin column -->
          <template #item.plugin_id="{ item }">
            <span
              v-if="item.plugin_id"
              class="text-caption font-weight-medium"
            >
              {{ item.plugin_id }}
            </span>
            <span
              v-else
              class="text-medium-emphasis text-caption"
            >—</span>
          </template>

          <!-- Active status column -->
          <template #item.active="{ item }">
            <v-chip
              :color="item.active ? 'primary' : ''"
              size="default"
              variant="flat"
            >
              <v-icon
                :icon="item.active ? 'mdi-check-circle' : 'mdi-close-circle'"
                size="small"
                class="me-1"
              />
              {{ item.active ? 'Aktív' : 'Inaktív' }}
            </v-chip>
          </template>

          <!-- Actions column -->
          <template #item.actions="{ item }">
            <div class="d-flex ga-2">
              <v-tooltip :text="item.active ? 'Üzlet deaktiválása' : 'Üzlet aktiválása'">
                <template #activator="{ props }">
                  <v-btn
                    v-bind="props"
                    :icon="item.active ? 'mdi-toggle-switch' : 'mdi-toggle-switch-off'"
                    color="primary"
                    variant="text"
                    :loading="toggleLoading === item.id"
                    @click.stop="toggleActivation(item)"
                  />
                </template>
              </v-tooltip>
            </div>
          </template>

          <!-- Empty state -->
          <template #no-data>
            <div class="text-center pa-8">
              <v-icon
                size="64"
                color="grey-lighten-2"
                class="mb-4"
              >
                mdi-store-off
              </v-icon>
              <div class="text-h6 text-medium-emphasis mb-2">
                Nincs üzlet
              </div>
              <div class="text-body-2 text-medium-emphasis mb-4">
                Még nem található üzlet a rendszerben
              </div>
              <v-btn
                color="primary"
                variant="elevated"
                prepend-icon="mdi-store-plus"
                @click="addVendor"
              >
                Első üzlet hozzáadása
              </v-btn>
            </div>
          </template>
        </v-data-table>
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
          Üzletek betöltése...
        </div>
      </v-col>
    </v-row>

    <!-- Activation confirmation dialog -->
    <v-dialog
      v-model="activationDialog"
      max-width="400"
      :fullscreen="$vuetify.display.mobile"
      :transition="$vuetify.display.mobile ? 'dialog-bottom-transition' : 'dialog-transition'"
    >
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon
            :icon="selectedVendor?.active ? 'mdi-toggle-switch-off' : 'mdi-toggle-switch'"
            :color="selectedVendor?.active ? 'warning' : 'success'"
            class="me-2"
          />
          <span class="text-h6">
            Üzlet {{ selectedVendor?.active ? 'deaktiválása' : 'aktiválása' }}
          </span>
          <v-spacer />
          <v-btn
            v-if="$vuetify.display.mobile"
            icon="mdi-close"
            variant="text"
            @click="activationDialog = false"
          />
        </v-card-title>

        <v-card-text class="py-4">
          <div class="text-body-1 mb-4">
            Biztosan {{ selectedVendor?.active ? 'deaktiválni' : 'aktiválni' }}
            szeretnéd a <strong class="text-primary">{{ selectedVendor?.name }}</strong>
            üzletet?
          </div>

          <v-alert
            :type="selectedVendor?.active ? 'warning' : 'info'"
            variant="tonal"
            class="mb-2"
          >
            <div v-if="selectedVendor?.active">
              A deaktiválás után az üzlet nem lesz elérhető a felhasználók számára.
            </div>
            <div v-else>
              Az aktiválás után az üzlet ismét elérhető lesz a felhasználók számára.
            </div>
          </v-alert>
        </v-card-text>

        <v-card-actions class="pa-4">
          <v-spacer v-if="!$vuetify.display.mobile" />
          <v-btn
            :block="$vuetify.display.mobile"
            color="grey-darken-1"
            variant="outlined"
            class="mb-2 mb-sm-0"
            @click="activationDialog = false"
          >
            Mégse
          </v-btn>
          <v-btn
            :block="$vuetify.display.mobile"
            :color="selectedVendor?.active ? 'warning' : 'success'"
            variant="flat"
            :loading="toggleLoading === selectedVendor?.id"
            @click="confirmToggleActivation"
          >
            {{ selectedVendor?.active ? 'Deaktiválás' : 'Aktiválás' }}
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useVendorStore } from "@/stores/vendor"

// Composables
const router = useRouter()
const vendorStore = useVendorStore()

// Reactive data
const allVendorList = ref([])
const isLoading = ref(true)
const toggleLoading = ref(null)
const activationDialog = ref(false)
const selectedVendor = ref(null)
const snackbar = ref({
  show: false,
  text: '',
  color: 'success'
})

// Table headers configuration
const headers = [
  {
    title: '#',
    key: 'index',
    align: 'start',
    sortable: false,
    width: '80px'
  },
  {
    title: 'Név',
    key: 'name',
    align: 'start',
    sortable: true,
    minWidth: '200px'
  },
  {
    title: 'Típus',
    key: 'menu_type',
    align: 'center',
    sortable: true,
    width: '160px'
  },
  {
    title: 'Plugin',
    key: 'plugin_id',
    align: 'center',
    sortable: true,
    width: '160px'
  },
  {
    title: 'Állapot',
    key: 'active',
    align: 'center',
    sortable: true,
    width: '140px'
  },
  {
    title: 'Műveletek',
    key: 'actions',
    align: 'center',
    sortable: false,
    width: '100px'
  }
]

// Methods
const refreshVendorList = async () => {
  try {
    isLoading.value = true


    const response = await vendorStore.fetch()
    if (response?.data?.data) {
      allVendorList.value = response.data.data
    }
  } catch (error) {
    showSnackbar('Hiba történt az üzletek betöltése során', 'error')
    console.error('Error fetching vendors:', error)
  } finally {
    isLoading.value = false
  }
}

const toggleActivation = (vendor) => {
  selectedVendor.value = vendor
  activationDialog.value = true
}

const confirmToggleActivation = async () => {
  if (!selectedVendor.value) return

  try {
    toggleLoading.value = selectedVendor.value.id

    if (selectedVendor.value.active) {
      await vendorStore.deactivate(selectedVendor.value.id)
      showSnackbar(`${selectedVendor.value.name} deaktiválva`, 'warning')
    } else {
      await vendorStore.activate(selectedVendor.value.id)
      showSnackbar(`${selectedVendor.value.name} aktiválva`, 'success')
    }

    // Refresh the list to get updated data
    await refreshVendorList()

  } catch (error) {
    const action = selectedVendor.value.active ? 'deaktiválása' : 'aktiválása'
    showSnackbar(`Hiba történt az üzlet ${action} során`, 'error')
    console.error('Error toggling vendor activation:', error)
  } finally {
    toggleLoading.value = null
    activationDialog.value = false
    selectedVendor.value = null
  }
}

const openVendorConfiguration = (vendorId) => {
  const vendor = allVendorList.value.find(v => v.id === vendorId)
  if (vendor) {
    vendorStore.selectedVendor = vendor
  }
  router.push({ path: `/admin/${vendorId}/config` })
}

const openVendorMenuManager = (vendorId) => {
  const vendor = allVendorList.value.find(v => v.id === vendorId)
  if (vendor) {
    vendorStore.selectedVendor = vendor
  }
  router.push({ path: `/admin/${vendorId}/menu` })
}

const addVendor = () => {
  router.push({ path: '/admin/add' })
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
  refreshVendorList()
})
</script>

<style scoped>
:deep(.vendor-table .v-data-table__tr) {
  cursor: pointer;
}
</style>
