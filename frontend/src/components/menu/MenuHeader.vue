<template>
  <v-row class="pa-2">
    <!-- Vendor Title -->
    <v-col
      class="d-flex justify-content-center justify-content-xl-start"
      cols="12"
    >
      <h2>{{ vendorTitle }}</h2>
    </v-col>

    <!-- Order State -->
    <v-col
      sm="auto"
      class="d-flex flex-fill align-items-center justify-content-sm-start justify-content-center justify-content-xl-start"
    >
      <OrderState class="text-truncate my-auto" />
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
          :enable_email_order="vendorSettings.enable_email_order"
          :enable_full_automatic_order="vendorSettings.enable_full_automatic_order"
          :enable_manual_order="vendorSettings.enable_manual_order"
        />
      </div>
    </v-col>
  </v-row>
</template>

<script setup>
import OrderState from '@/components/menu/OrderState.vue'
import AutoEmailOrderInfo from '@/components/menu/AutoOrderInfo.vue'
// import NotificationToggle from '@/components/NotificationToggle.vue'
// import VendorLinkButton from '@/components/VendorLinkButton.vue'
import TransferPopup from '@/components/TransferPopup.vue'

// Props
const prop = defineProps({
  vendorTitle: {
    type: String,
    required: true
  },
  vendorSettings: {
    type: Object,
    required: true
  },
  userCount: {
    type: Number,
    required: true
  },
  vendorLink: {
    type: String,
    default: ''
  },
  notificationStatus: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['subscribe', 'unsubscribe-requested'])

const handleToggle = () => {
  if (prop.notificationStatus) {
    emit('unsubscribe-requested')
    return
  }

  if (!('Notification' in window)) {
    return
  }

  if (Notification.permission === 'denied') {
    // Browser has blocked notifications — inform the parent to show a message
    emit('subscribe', { blocked: true })
    return
  }

  if (Notification.permission === 'default') {
    // Request permission synchronously within the user gesture call stack
    Notification.requestPermission().then(permission => {
      if (permission === 'granted') {
        emit('subscribe', { blocked: false })
      }
    })
    return
  }

  // Already granted
  emit('subscribe', { blocked: false })
}
</script>
