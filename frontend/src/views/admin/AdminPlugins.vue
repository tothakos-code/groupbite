<template>
  <v-container
    fluid
    class="pa-2 pa-md-4"
  >
    <v-row class="mb-4">
      <v-col class="d-flex align-center">
        <h1 class="text-h4">
          Pluginok
        </h1>
      </v-col>
      <v-col class="d-flex justify-end">
        <v-tooltip text="Lista frissítése">
          <template #activator="{ props }">
            <v-btn
              v-bind="props"
              icon="mdi-refresh"
              color="primary"
              variant="elevated"
              size="small"
              :loading="isLoading"
              @click="load"
            />
          </template>
        </v-tooltip>
      </v-col>
    </v-row>

    <v-skeleton-loader
      v-if="isLoading"
      type="card@3"
    />

    <v-alert
      v-else-if="error"
      type="error"
      variant="tonal"
      class="mb-4"
    >
      {{ error }}
    </v-alert>

    <template v-else>
      <v-card
        v-if="plugins.length === 0"
        class="text-center pa-8"
      >
        <v-icon
          size="64"
          color="grey-lighten-2"
          class="mb-4"
        >
          mdi-puzzle-outline
        </v-icon>
        <div class="text-h6 text-medium-emphasis mb-2">
          Nincs betöltött plugin
        </div>
        <div class="text-body-2 text-medium-emphasis">
          Helyezz el egy plugin mappát a <code>/plugins</code> könyvtárba és indítsd újra a szervert.
        </div>
      </v-card>

      <v-row v-else>
        <v-col
          v-for="plugin in plugins"
          :key="plugin.id"
          cols="12"
          md="6"
          lg="4"
        >
          <v-card elevation="2">
            <v-card-title class="d-flex align-center ga-2">
              <v-icon color="secondary">
                mdi-puzzle
              </v-icon>
              <span class="text-subtitle-1 font-weight-bold">{{ plugin.id }}</span>
              <v-spacer />
              <v-chip
                size="small"
                color="success"
                variant="tonal"
              >
                Betöltve
              </v-chip>
            </v-card-title>

            <v-divider />

            <v-card-text>
              <div class="text-caption text-medium-emphasis mb-2">
                Hozzárendelt üzletek:
              </div>
              <div v-if="vendorsForPlugin(plugin.id).length > 0">
                <v-chip
                  v-for="vendor in vendorsForPlugin(plugin.id)"
                  :key="vendor.id"
                  size="small"
                  variant="outlined"
                  color="primary"
                  class="me-1 mb-1"
                  :to="`/admin/${vendor.id}/config`"
                >
                  {{ vendor.name }}
                </v-chip>
              </div>
              <div
                v-else
                class="text-medium-emphasis text-caption"
              >
                Nincs hozzárendelt üzlet
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useVendorStore } from '@/stores/vendor'

const vendorStore = useVendorStore()

const plugins = ref([])
const vendors = ref([])
const isLoading = ref(true)
const error = ref(null)

const vendorsForPlugin = (pluginId) =>
  vendors.value.filter(v => v.plugin_id === pluginId)

async function load() {
  isLoading.value = true
  error.value = null
  try {
    const [pluginRes, vendorRes] = await Promise.all([
      axios.get('/api/plugins'),
      vendorStore.fetch(),
    ])
    plugins.value = pluginRes.data?.data ?? []
    vendors.value = vendorRes.data?.data ?? []
  } catch (e) {
    error.value = 'Hiba a pluginok betöltése során'
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

onMounted(load)
</script>
