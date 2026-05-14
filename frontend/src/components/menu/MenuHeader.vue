<template>
  <v-row class="pa-2">
    <!-- Vendor Title -->
    <v-col
      class="d-flex justify-content-center justify-content-xl-start"
      cols="12"
    >
      <h2>{{ vendorTitle }}</h2>
    </v-col>

    <!-- Order State + Date Range -->
    <v-col
      v-if="orderStore.order?.id"
      sm="auto"
      class="d-flex flex-fill align-items-center justify-content-sm-start justify-content-center justify-content-xl-start"
    >
      <OrderState class="text-truncate my-auto" />
      <span
        v-if="orderDateRange"
        class="text-caption text-medium-emphasis ms-2 my-auto"
      >
        {{ orderDateRange }}
      </span>
    </v-col>

    <!-- Auto Email Order Info -->
    <v-col
      v-if="vendorSettings.auto_email_order && vendorSettings.closed_scheduler_active"
      sm="auto"
      class="d-flex flex-fill align-items-center justify-content-sm-start justify-content-center"
    >
      <AutoEmailOrderInfo
        :deadline="vendorSettings.closed_scheduler"
        :min-users="vendorSettings.email_min_user"
        :current-users="userCount"
      />
    </v-col>

    <!-- Action Buttons -->
    <v-col
      sm="auto"
      class="d-flex justify-content-center justify-content-xl-end align-items-center"
    >
      <div class="d-flex">
        <v-tooltip
          v-if="vendorSettings.show_notification_button"
          location="bottom"
        >
          <template #activator="{ props: props }">
            <v-btn
              v-bind="props"
              :icon="notificationStatus ? 'mdi-bell' : 'mdi-bell-off'"
              color="primary"
              size="small"
              variant="elevated"
              class="me-2"
              @click="handleToggle"
            />
          </template>
          <span>{{ notificationStatus ? 'Értesítés kikapcsolása' : 'Értesítés bekapcsolása ezen az eszközön' }}</span>
        </v-tooltip>

        <v-tooltip
          v-if="vendorLink"
          location="bottom"
        >
          <template #activator="{ props }">
            <v-btn
              v-bind="props"
              :href="vendorLink"
              target="_blank"
              color="primary"
              variant="elevated"
              class="me-2"
            >
              Eredeti oldal
              <v-icon
                icon="mdi-open-in-new"
                end
                size="small"
              />
            </v-btn>
          </template>
          <span>Eredeti étterem oldala megnyitás új lapon</span>
        </v-tooltip>

        <TransferPopup
          v-if="vendorSettings.enable_email_order || vendorSettings.enable_full_automatic_order || vendorSettings.enable_manual_order"
          :enable-email-order="vendorSettings.enable_email_order"
          :enable-full-automatic-order="vendorSettings.enable_full_automatic_order"
          :enable-manual-order="vendorSettings.enable_manual_order"
        />

        <v-btn
          v-if="auth.user?.admin && menuType === 'own_inventory'"
          color="primary"
          variant="elevated"
          size="small"
          class="ms-2"
          prepend-icon="mdi-chart-line"
          @click="router.push({ name: 'stats', params: { vendorId } })"
        >
          {{ $t('stats.button.label') }}
        </v-btn>
      </div>
    </v-col>
  </v-row>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import OrderState from '@/components/menu/OrderState.vue'
import AutoEmailOrderInfo from '@/components/menu/AutoOrderInfo.vue'
import TransferPopup from '@/components/TransferPopup.vue'
import { useOrderStore } from '@/stores/order'
import { useAuth } from '@/stores/auth'

const orderStore = useOrderStore()
const auth = useAuth()
const router = useRouter()

const prop = defineProps({
  vendorTitle: { type: String, required: true },
  vendorId: { type: String, default: '' },
  vendorSettings: { type: Object, required: true },
  userCount: { type: Number, required: true },
  vendorLink: { type: String, default: '' },
  notificationStatus: { type: Boolean, default: false },
  menuType: { type: String, default: '' },
})

const emit = defineEmits(['subscribe', 'unsubscribe-requested'])

const orderDateRange = computed(() => {
  const order = orderStore.order
  if (!order?.open_from) return null
  if (!order.open_until || order.open_until === order.open_from) return null
  return `${order.open_from} – ${order.open_until}`
})

const handleToggle = () => {
  if (prop.notificationStatus) {
    emit('unsubscribe-requested')
    return
  }

  if (!('Notification' in window)) return

  if (Notification.permission === 'denied') {
    emit('subscribe', { blocked: true })
    return
  }

  if (Notification.permission === 'default') {
    Notification.requestPermission().then(permission => {
      if (permission === 'granted') {
        emit('subscribe', { blocked: false })
      }
    })
    return
  }

  emit('subscribe', { blocked: false })
}
</script>
