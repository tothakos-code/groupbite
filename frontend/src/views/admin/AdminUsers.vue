<template>
  <router-view />
  <v-container
    v-if="auth.isLoggedIn && !$route.params.userId"
    fluid
    class="pa-2 pa-md-4"
  >
    <!-- Header -->
    <v-row class="mb-4">
      <v-col>
        <h1 class="text-h4 text-md-h4">
          Felhasználók
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
          v-for="user in users"
          :key="user.id"
          class="mb-3"
          elevation="2"
        >
          <v-card-text class="pb-2">
            <div class="d-flex justify-space-between align-center mb-2">
              <div class="text-subtitle-1 font-weight-medium">
                {{ user.username }}
              </div>
              <v-chip
                :color="user.admin ? 'success' : 'default'"
                :variant="user.admin ? 'flat' : 'outlined'"
                size="small"
              >
                {{ user.admin ? 'Admin' : 'User' }}
              </v-chip>
            </div>
            <div class="text-body-2 text-medium-emphasis mb-3">
              {{ user.email }}
            </div>
          </v-card-text>

          <v-card-actions class="pt-0">
            <v-btn
              :color="user.admin ? 'warning' : 'primary'"
              :prepend-icon="user.admin ? 'mdi-shield-account' : 'mdi-shield-account-outline'"
              variant="text"
              size="small"
              @click="toggleAdminStatus(user)"
            >
              {{ user.admin ? 'Admin eltávolítás' : 'Admin hozzáadás' }}
            </v-btn>

            <v-spacer />

            <v-btn
              icon="mdi-format-list-bulleted"
              color="info"
              variant="text"
              size="small"
              @click="viewUserOrders(user)"
            />
            <v-btn
              icon="mdi-cog"
              color="grey"
              variant="text"
              size="small"
              @click="openUserSettings(user)"
            />
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
          :items="users"
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
          <!-- Admin status column -->
          <template #item.admin="{ item }">
            <v-chip
              :color="item.admin ? 'primary' : 'default'"
              :variant="item.admin ? 'flat' : 'outlined'"
              size="small"
            >
              {{ item.admin ? 'Admin' : 'User' }}
            </v-chip>
          </template>

          <!-- Actions column -->
          <template #item.actions="{ item }">
            <div class="d-flex ga-2">
              <v-tooltip text="Admin jogosultság ki/be kapcsolása">
                <template #activator="{ props }">
                  <v-btn
                    v-bind="props"
                    :icon="item.admin ? 'mdi-shield-account' : 'mdi-shield-account-outline'"
                    color="primary"
                    variant="text"
                    size="small"
                    @click="toggleAdminStatus(item)"
                  />
                </template>
              </v-tooltip>

              <v-tooltip text="Felhasználó rendelései">
                <template #activator="{ props }">
                  <v-btn
                    v-bind="props"
                    icon="mdi-format-list-bulleted"
                    color="primary"
                    variant="text"
                    size="small"
                    @click="viewUserOrders(item)"
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
          Felhasználók betöltése...
        </div>
      </v-col>
    </v-row>

    <!-- Confirmation dialog -->
    <v-dialog
      v-model="confirmDialog"
      max-width="400"
      :fullscreen="$vuetify.display.mobile"
      :transition="$vuetify.display.mobile ? 'dialog-bottom-transition' : 'dialog-transition'"
    >
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon class="me-2">
            mdi-help-circle
          </v-icon>
          <span class="text-h6">Megerősítés</span>
          <v-spacer />
          <v-btn
            v-if="$vuetify.display.mobile"
            icon="mdi-close"
            variant="text"
            @click="confirmDialog = false"
          />
        </v-card-title>

        <v-card-text class="py-4">
          <div class="text-body-1">
            Biztosan {{ selectedUser?.admin ? 'elveszed' : 'megadod' }} az admin jogosultságot
            <strong class="text-primary">{{ selectedUser?.username }}</strong> felhasználónak?
          </div>
        </v-card-text>

        <v-card-actions class="pa-4">
          <v-spacer v-if="!$vuetify.display.mobile" />
          <v-btn
            :block="$vuetify.display.mobile"
            color="grey-darken-1"
            variant="outlined"
            class="mb-2 mb-sm-0"
            @click="confirmDialog = false"
          >
            Mégse
          </v-btn>
          <v-btn
            :block="$vuetify.display.mobile"
            :color="selectedUser?.admin ? 'warning' : 'primary'"
            variant="flat"
            @click="confirmToggleAdmin"
          >
            {{ selectedUser?.admin ? 'Elveszed' : 'Megadod' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useAuth } from "@/stores/auth"
import { useRouter } from 'vue-router'
import { notify } from "@kyvg/vue3-notification";
// Composables
const auth = useAuth()
const router = useRouter()

// Reactive data
const users = ref([])
const isLoading = ref(true)
const page = ref(1)
const itemsPerPage = ref(10)
const totalItems = ref(0)
const confirmDialog = ref(false)
const selectedUser = ref(null)

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
    title: 'Felhasználónév',
    key: 'username',
    align: 'start',
    sortable: true,
    minWidth: '150px'
  },
  {
    title: 'Email',
    key: 'email',
    align: 'start',
    sortable: true,
    minWidth: '200px'
  },
  {
    title: 'Státusz',
    key: 'admin',
    align: 'center',
    sortable: true,
    width: '120px'
  },
  {
    title: 'Műveletek',
    key: 'actions',
    align: 'center',
    sortable: false,
    width: '180px'
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
  refreshUsersList()
})

// Methods
const updatePage = (newPage) => {
  page.value = newPage
}

const updateItemsPerPage = (newItemsPerPage) => {
  itemsPerPage.value = newItemsPerPage
  page.value = 1 // Reset to first page when changing items per page
}

const refreshUsersList = async () => {
  try {
    isLoading.value = true
    const response = await auth.fetchAll({
      limit: itemsPerPage.value === -1 ? 1000 : itemsPerPage.value, // Handle "show all"
      page: page.value
    })

    if (response.status === 200) {
      users.value = response.data.data.items
      totalItems.value = response.data.data.total_count

      // Update pagination info from server if needed
      if (response.data.data.page !== page.value) {
        page.value = response.data.data.page
      }
    }
  } catch (error) {
    notify({
      type: "error",
      text: 'Hiba történt a felhasználók betöltése során',
    });
    console.error('Error fetching users:', error)
  } finally {
    isLoading.value = false
  }
}

const toggleAdminStatus = (user) => {
  selectedUser.value = user
  confirmDialog.value = true
}

const confirmToggleAdmin = async () => {
  try {
    const response = await auth.promote(selectedUser.value.id)

    if (response.status === 200) {

      selectedUser.value.admin = !selectedUser.value.admin

      const message = selectedUser.value.admin
        ? `${selectedUser.value.username} admin jogosultságot kapott`
        : `${selectedUser.value.username} admin jogosultsága elvéve`

      notify({
        type: "success",
        text: message,
      });
      confirmDialog.value = false
      selectedUser.value = null
    }
  } catch (error) {
    notify({
      type: "error",
      text: 'Hiba történt a jogosultság módosítása során',
    });
    console.error('Error toggling admin status:', error)
  }
}

const viewUserOrders = (user) => {
  console.log('View orders for user:', user.username)
  notify({
    type: "info",
    text: `${user.username} rendeléseinek megtekintése`,
  });
  router.push({ path:`/admin/users/${user.id}/history`})
}

// Lifecycle
onMounted(() => {
  refreshUsersList()
})
</script>

<style scoped>
/* Using Vuetify's built-in spacing classes */
</style>
