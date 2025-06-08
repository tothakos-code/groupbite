<template>
  <v-card
    :variant="isSelected ? 'flat' : 'outlined'"
    :color="isSelected ? 'success' : 'grey-lighten-5'"
    :class="[
      'order-card',
      'mb-2',
      'cursor-pointer',
      { 'selected': isSelected }
    ]"
    elevation="2"
    @click="$emit('click')"
  >
    <v-card-text class="pa-3">
      <!-- Header Row -->
      <v-row
        align="center"
        no-gutters
        class="mb-2"
      >
        <!-- Selection Indicator -->
        <v-col cols="auto">
          <v-icon
            :color="isSelected ? 'white' : 'grey-darken-1'"
            size="large"
            class="me-3"
          >
            {{ isSelected ? 'mdi-check-circle' : 'mdi-circle-outline' }}
          </v-icon>
        </v-col>

        <!-- Vendor Info -->
        <v-col>
          <div class="d-flex align-center">
            <v-avatar
              size="32"
              :color="isSelected ? 'success-darken-1' : 'primary'"
              class="me-2"
            >
              <v-icon
                color="white"
                size="small"
              >
                mdi-store
              </v-icon>
            </v-avatar>
            <div>
              <div
                class="text-h6 font-weight-bold"
                :class="isSelected ? 'text-white' : 'text-grey-darken-2'"
              >
                {{ order.vendor }}
              </div>
              <div
                class="text-caption"
                :class="isSelected ? 'text-success-lighten-4' : 'text-grey-lighten-1'"
              >
                {{ formatDate(order.date_of_order) }}
              </div>
            </div>
          </div>
        </v-col>

        <!-- Navigate Button -->
        <v-col cols="auto">
          <v-btn
            icon
            variant="text"
            :color="isSelected ? 'white' : 'grey-darken-1'"
            size="small"
            @click.stop="goToOrder(order)"
          >
            <v-icon>mdi-open-in-new</v-icon>
            <v-tooltip
              activator="parent"
              location="top"
            >
              Rendelés megnyitása
            </v-tooltip>
          </v-btn>
        </v-col>
      </v-row>

      <!-- Order Details Row -->
      <v-row
        align="center"
        no-gutters
      >
        <!-- Order Status -->
        <v-col
          cols="auto"
          class="me-4"
        >
          <v-chip
            :color="getStatusColor(order.state_id)"
            size="small"
            variant="flat"
          >
            <template #prepend>
              <v-icon size="small">
                {{ getStatusIcon(order.state_id) }}
              </v-icon>
            </template>
            {{ getStatusText(order.state_id) }}
          </v-chip>
        </v-col>

        <!-- User Participation -->
        <v-col
          v-if="order.ordered"
          cols="auto"
          class="me-4"
        >
          <v-chip
            color="warning"
            size="small"
            variant="tonal"
          >
            <template #prepend>
              <v-icon size="small">
                mdi-basket
              </v-icon>
            </template>
            Rendeltél
          </v-chip>
        </v-col>

        <!-- Order Value -->
        <v-col>
          <div class="text-end">
            <div
              class="text-body-1 font-weight-bold"
              :class="isSelected ? 'text-white' : 'text-grey-darken-2'"
            >
              {{ formatCurrency(order.sum || 0) }}
            </div>
            <div
              class="text-caption"
              :class="isSelected ? 'text-success-lighten-4' : 'text-grey-lighten-1'"
            >
              {{ getParticipantCount(order) }} résztvevő
            </div>
          </div>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: 'InformativeOrderCard',
  props: {
    order: {
      type: Object,
      required: true
    },
    isSelected: {
      type: Boolean,
      default: false
    }
  },
  emits: ['click'],
  methods: {
    formatCurrency(amount) {
      return new Intl.NumberFormat('hu-HU', {
        style: 'currency',
        currency: 'HUF',
        minimumFractionDigits: 0
      }).format(amount);
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('hu-HU', {
        month: 'short',
        day: 'numeric',
        weekday: 'short'
      });
    },
    getStatusColor(stateId) {
      switch (stateId) {
        case 'closed': return 'error';
        case 'order': return 'warning';
        case 'collect': return 'success';
        default: return 'grey';
      }
    },
    getStatusIcon(stateId) {
      switch (stateId) {
        case 'closed': return 'mdi-lock';
        case 'order': return 'mdi-clock-outline';
        case 'collect': return 'mdi-lock-open-variant';
        default: return 'mdi-help-circle';
      }
    },
    getStatusText(stateId) {
      switch (stateId) {
        case 'closed': return 'Lezárva';
        case 'order': return 'Rendelés';
        case 'collect': return 'Gyűjtés';
        default: return 'Ismeretlen';
      }
    },
    getParticipantCount(order) {
      if (order.basket && typeof order.basket === 'object') {
        return Object.keys(order.basket).length;
      }
      return 0;
    },
    goToOrder(order) {
      this.$router.push({ path: "/menu/" + order.vendor + "/" + order.date_of_order })
    },
  }
}
</script>

<style scoped>
.order-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 12px !important;
  position: relative;
  overflow: hidden;
}

.order-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
}

.order-card.selected {
  transform: scale(1.02);
  box-shadow: 0 8px 25px rgba(76, 175, 80, 0.3) !important;
}

.cursor-pointer {
  cursor: pointer;
}

.order-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg,
    var(--v-theme-primary),
    var(--v-theme-secondary)
  );
  opacity: 0;
  transition: opacity 0.3s ease;
}

.order-card.selected::before {
  opacity: 1;
}

.text-success-lighten-4 {
  color: rgba(255, 255, 255, 0.7) !important;
}
</style>
