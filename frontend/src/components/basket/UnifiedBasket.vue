<template>
  <v-card
    class="unified-basket"
    elevation="2"
    rounded="lg"
  >
    <!-- Header -->
    <v-card-title class="bg-primary text-white pa-3">
      <v-row
        align="center"
        no-gutters
      >
        <v-col cols="auto">
          <v-icon
            size="32"
            class="me-2"
          >
            mdi-cart
          </v-icon>
        </v-col>
        <v-col class="d-none d-sm-flex">
          <h2 class="text-h5 font-weight-bold">
            Kosarak
          </h2>
        </v-col>
        <v-spacer />
        <v-col
          cols="auto"
          class="text-end"
        >
          <div class="d-flex align-center">
            <v-icon class="me-1">
              mdi-cash-multiple
            </v-icon>
            <span class="text-h6 font-weight-bold">{{ orderStore.totalSum }} Ft</span>
          </div>
          <div class="d-flex align-center mt-1">
            <v-icon
              class="me-1"
              size="small"
            >
              mdi-account-group
            </v-icon>
            <span class="text-caption">{{ orderStore.userCount }} fő</span>
          </div>
        </v-col>
      </v-row>
    </v-card-title>

    <v-card-text class="pa-0">
      <!-- No order: centered call-to-action -->
      <div
        v-if="!orderStore.order?.id"
        class="no-order-state text-center py-12 px-4"
      >
        <v-icon
          size="64"
          color="grey-lighten-2"
          class="mb-4"
        >
          mdi-cart-off
        </v-icon>
        <p class="text-h6 text-grey mb-1">
          Nincs nyitott rendelés
        </p>
        <p
          v-if="showButton"
          class="text-body-2 text-grey-lighten-1 mb-6"
        >
          Indíts rendelést, hogy te és csapatod elkezdhessen rendelni.
        </p>
        <p
          v-else
          class="text-body-2 text-grey-lighten-1 mb-2"
        >
          A rendelés automatikusan nyílik meg ezen a napon.
        </p>
        <v-btn
          v-if="showButton"
          color="primary"
          variant="elevated"
          prepend-icon="mdi-plus-circle"
          @click="orderStore.showCreateOrderDialog = true"
        >
          Rendelés indítása
        </v-btn>
      </div>

      <!-- Active order: normal basket content -->
      <template v-else>
        <!-- Current User's Basket (Full Featured) -->
        <CurrentUserBasket
          :user-basket="orderStore.userBasket"
          :user-basket-sum="orderStore.userBasketSum"
          :transport-fee="orderStore.transportFeePerPerson"
          :is-empty="orderStore.isUserBasketEmpty"
          @clear-basket="orderStore.clearBasket"
          @remove-item="orderStore.removeItem"
        />

        <!-- Other Users' Baskets (Compact) -->
        <v-divider />

        <div class="other-users-section">
          <div class="other-users-header bg-surface px-4 py-2 d-flex align-center justify-space-between">
            <div class="d-flex align-center">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-account-multiple
              </v-icon>
              <span class="text-subtitle-2 font-weight-medium">
                Többi rendelő ({{ otherUsersBaskets.length }})
              </span>
            </div>

            <div
              v-if="otherUsersBaskets.length > 0"
              class="d-flex align-center"
            >
              <v-btn
                variant="text"
                size="small"
                color="primary"
                @click="expandAll"
              >
                <v-icon
                  class="me-1"
                  size="small"
                >
                  mdi-arrow-expand-all
                </v-icon>
                Mind kinyit
              </v-btn>
              <v-btn
                variant="text"
                size="small"
                color="primary"
                class="ms-1"
                @click="collapseAll"
              >
                <v-icon
                  class="me-1"
                  size="small"
                >
                  mdi-arrow-collapse-all
                </v-icon>
                Mind bezár
              </v-btn>
            </div>
          </div>

          <div
            v-if="otherUsersBaskets.length === 0"
            class="text-center py-6"
          >
            <v-icon
              size="48"
              color="grey-lighten-1"
            >
              mdi-account-plus
            </v-icon>
            <p class="text-grey-lighten-1 mt-2">
              Még senki más nem rendelt
            </p>
          </div>

          <UserBasket
            v-for="userEntry in otherUsersBaskets"
            :key="userEntry.user_id"
            ref="compactBaskets"
            :username="userEntry.username"
            :user-id="userEntry.user_id"
            :user-basket="userEntry.items"
            :transport-fee="orderStore.transportFeePerPerson"
            :copyable="true"
            :initially-expanded="true"
            @copy-basket="orderStore.copy"
          />
        </div>
      </template>
    </v-card-text>
  </v-card>

  <!-- Start Order Dialog -->
  <v-dialog
    v-model="orderStore.showCreateOrderDialog"
    :max-width="$vuetify.display.smAndUp ? 500 : 360"
  >
    <v-card>
      <v-card-title class="pa-4 pb-2">
        Rendelés indítása
      </v-card-title>

      <v-card-text class="pa-0">
        <!-- Landscape on sm+ (side-by-side), portrait on xs (stacked) -->
        <div
          class="d-flex"
          :class="$vuetify.display.smAndUp ? 'flex-row' : 'flex-column'"
          style="min-height: 160px"
        >
          <!-- Date pane -->
          <div
            class="d-flex flex-column align-center justify-center pa-5 text-center"
            :style="$vuetify.display.smAndUp
              ? 'width: 44%; min-width: 44%; border-right: 1px solid rgba(var(--v-border-color), var(--v-border-opacity))'
              : 'border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity))'"
          >
            <v-icon
              size="36"
              color="primary"
              class="mb-2"
            >
              mdi-calendar-clock
            </v-icon>
            <div class="text-subtitle-2 font-weight-bold">
              {{ formattedSelectedDate }}
            </div>
            <div class="text-caption text-medium-emphasis mt-1">
              Rendelés napja
            </div>
          </div>

          <!-- Time pane -->
          <div class="flex-grow-1 pa-5 d-flex flex-column justify-center">
            <div class="text-caption text-medium-emphasis mb-3">
              Záróidőpont
            </div>
            <v-text-field
              v-model="newOrderUntilTime"
              type="time"
              variant="outlined"
              density="comfortable"
              prepend-inner-icon="mdi-clock-outline"
              hide-details="auto"
            />
            <div class="text-caption text-medium-emphasis mt-2">
              Megadott időpontkor automatikusan lezárul
            </div>
          </div>
        </div>

        <v-alert
          v-if="startOrderError"
          type="error"
          density="compact"
          class="ma-3 mt-0"
        >
          {{ startOrderError }}
        </v-alert>
      </v-card-text>

      <v-card-actions class="pa-4 pt-2">
        <v-spacer />
        <v-btn
          variant="text"
          @click="() => { orderStore.pendingItem = null; closeStartOrderDialog() }"
        >
          Mégsem
        </v-btn>
        <v-btn
          color="primary"
          variant="elevated"
          :loading="orderStore.isLoading"
          @click="submitStartOrder"
        >
          Indítás
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { notify } from '@kyvg/vue3-notification'
import { useAuth } from "@/stores/auth"
import { useOrderStore } from "@/stores/order"
import { useVendorStore } from "@/stores/vendor"
import { state as socketState } from '@/socket'
import CurrentUserBasket from './CurrentUserBasket.vue'
import UserBasket from './UserBasket.vue'

// Stores
const auth = useAuth()
const orderStore = useOrderStore()
const vendorStore = useVendorStore()

// Start order dialog — driven by orderStore.showCreateOrderDialog so MenuItem can open it too
const newOrderUntilTime = ref(null)
const startOrderError = ref('')

function getSuggestedEndTime() {
  const d = new Date()
  d.setHours(d.getHours() + 1)
  const rounded = Math.round(d.getMinutes() / 15) * 15
  if (rounded === 60) {
    d.setHours(d.getHours() + 1)
    d.setMinutes(0)
  } else {
    d.setMinutes(rounded)
  }
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

watch(() => orderStore.showCreateOrderDialog, (isOpen) => {
  if (isOpen) newOrderUntilTime.value = getSuggestedEndTime()
})

const showButton = computed(() =>
  !vendorStore.selectedVendor?.settings?.auto_order_creation
)

const formattedSelectedDate = computed(() => {
  const d = socketState.selectedDate ? new Date(socketState.selectedDate) : new Date()
  return d.toLocaleDateString('hu-HU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long',
  })
})

function closeStartOrderDialog() {
  orderStore.showCreateOrderDialog = false
  newOrderUntilTime.value = null
  startOrderError.value = ''
}

function formatDateToISO(d) {
  if (!d) return null
  const date = new Date(d)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

async function submitStartOrder() {
  startOrderError.value = ''
  if (!newOrderUntilTime.value) {
    startOrderError.value = 'A záróidőpont megadása kötelező.'
    return
  }
  const dateStr = formatDateToISO(socketState.selectedDate)
  const openUntil = dateStr
    ? (newOrderUntilTime.value ? `${dateStr}T${newOrderUntilTime.value}` : dateStr)
    : null
  const vendorId = vendorStore.selectedVendor?.id
  const res = await orderStore.createOrder(vendorId, openUntil)
  if (res?.status === 200 || res?.status === 201) {
    if (orderStore.pendingItem) {
      const { menuItemId, sizeId, optionChoiceIds } = orderStore.pendingItem
      orderStore.pendingItem = null
      await orderStore.addItem(menuItemId, sizeId, optionChoiceIds || [])
    }
    closeStartOrderDialog()
    notify({ type: 'success', text: 'Rendelés sikeresen megnyitva!' })
  } else {
    const err = res?.data?.error
    if (err === 'overlapping_order') {
      startOrderError.value = 'Már létezik egy nyitott rendelés erre az időszakra.'
    } else if (err === 'open_until_before_today') {
      startOrderError.value = 'A határidő nem lehet a mai nap előtt.'
    } else if (err === 'open_until_required') {
      startOrderError.value = 'A záróidőpont megadása kötelező.'
    } else {
      startOrderError.value = 'Hiba történt a rendelés megnyitásakor.'
    }
  }
}

// Template refs
const compactBaskets = ref([])

// Methods for expand/collapse all
const expandAll = () => {
  compactBaskets.value.forEach(basket => {
    if (basket && basket.expand) {
      basket.expand()
    }
  })
}

const collapseAll = () => {
  compactBaskets.value.forEach(basket => {
    if (basket && basket.collapse) {
      basket.collapse()
    }
  })
}

// Computed properties
const otherUsersBaskets = computed(() => {
  if (!auth.isLoggedIn || !orderStore.basket) return []

  // Handle if basket is an array
  if (Array.isArray(orderStore.basket)) {
    return orderStore.basket.filter(user =>
      user.username !== auth.user.username
    )
  }

  // Handle if basket is an object with user entries
  if (typeof orderStore.basket === 'object') {
    return Object.values(orderStore.basket).filter(user =>
      user.username !== auth.user.username
    )
  }

  return []
})
</script>

<style scoped>
.unified-basket {
  width: 100%;
  max-width: 100%;
}

.other-users-section {
  background-color: rgb(var(--v-theme-surface));
  border: 1px solid rgb(var(--v-theme-outline-variant));
}

.other-users-header {
  border-bottom: 1px solid rgb(var(--v-theme-outline-variant));
}

.v-subheader {
  background-color: rgb(var(--v-theme-surface-bright));
  border-bottom: 1px solid rgb(var(--v-theme-outline-variant));
}
</style>
