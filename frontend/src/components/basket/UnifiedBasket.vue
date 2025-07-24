<template>
  <v-card
    class="unified-basket"
    elevation="2"
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
        <div class="other-users-header bg-surface-bright px-4 py-2 d-flex align-center justify-space-between">
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
    </v-card-text>
  </v-card>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useAuth } from "@/stores/auth"
import { useOrderStore } from "@/stores/order"
import CurrentUserBasket from './CurrentUserBasket.vue'
import UserBasket from './UserBasket.vue'

// Stores
const auth = useAuth()
const orderStore = useOrderStore()

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
