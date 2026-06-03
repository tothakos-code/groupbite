<template>
  <v-list
    density="compact"
    class="bg-surface summary-basket mx-2 mb-2 rounded-lg border"
  >
    <v-list-item
      v-for="(item, idx) in items"
      :key="idx"
      class="summary-item px-4 py-2"
    >
      <template #prepend>
        <v-chip
          color="secondary"
          size="x-small"
          variant="flat"
          class="me-3"
        >
          {{ item.count }}x
        </v-chip>
      </template>

      <v-list-item-title class="text-body-2">
        {{ item.item_name }}
        <span
          v-if="item.size_name"
          class="text-caption text-medium-emphasis"
        >
          ({{ item.size_name }})
        </span>
      </v-list-item-title>

      <v-list-item-subtitle
        v-if="(item.option_selections && item.option_selections.length) || item.extras_summary?.options?.length"
        class="text-caption text-medium-emphasis"
      >
        {{ (item.option_selections?.length ? item.option_selections : item.extras_summary?.options || []).map(s => s.choice).join(', ') }}
      </v-list-item-subtitle>

      <v-list-item-subtitle
        v-if="item.packaging_fee > 0"
        class="text-caption text-medium-emphasis"
      >
        + Csomagolási díj: {{ item.packaging_fee }} Ft
      </v-list-item-subtitle>

      <v-chip
        v-if="item.bundle_discount || item.extras_summary?.bundle"
        size="x-small"
        color="success"
        variant="tonal"
        prepend-icon="mdi-sale"
        class="mt-1"
      >
        {{ (item.bundle_discount || item.extras_summary?.bundle).name }}
      </v-chip>

      <template #append>
        <div class="text-end ms-2">
          <div
            v-if="item.bundle_discount || item.extras_summary?.bundle"
            class="text-caption text-medium-emphasis text-decoration-line-through"
          >
            {{ (item.bundle_discount || item.extras_summary?.bundle).original_price }} Ft
          </div>
          <span
            class="text-body-2 font-weight-medium"
            :class="(item.bundle_discount || item.extras_summary?.bundle) ? 'text-success' : ''"
          >
            {{ (item.effective_price ?? item.price) * item.count }} Ft
          </span>
        </div>
      </template>
    </v-list-item>

    <v-divider />
    <v-list-item class="px-4 py-2 bg-surface">
      <v-list-item-title class="text-caption text-medium-emphasis font-weight-medium">
        Összesen
      </v-list-item-title>
      <template #append>
        <span class="text-body-2 font-weight-bold">
          {{ grandTotal }} Ft
        </span>
      </template>
    </v-list-item>
  </v-list>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  items: {
    type: Array,
    required: true
  }
})

const grandTotal = computed(() =>
  props.items.reduce((sum, item) =>
    sum + (item.effective_price ?? item.price) * item.count, 0)
)
</script>

<style scoped>
.summary-basket {
  border: 1px solid rgb(var(--v-theme-outline-variant));
}

.summary-item {
  border-bottom: 1px solid rgb(var(--v-theme-outline-variant));
  background-color: rgb(var(--v-theme-surface));
}

.summary-item:last-child {
  border-bottom: none;
}
</style>
