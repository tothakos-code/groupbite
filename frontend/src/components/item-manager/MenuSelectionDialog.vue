<template>
  <v-dialog
    :model-value="modelValue"
    max-width="800"
    persistent
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <v-card>
      <v-card-title class="text-h6 bg-primary text-white">
        <v-icon class="me-2">
          mdi-menu
        </v-icon>
        {{ title }}
      </v-card-title>

      <v-card-text class="pa-4">
        <v-data-table
          v-model:selected="selectedItems"
          :headers="headers"
          :items="menus"
          :loading="loading"
          item-key="id"
          return-object
          single-select
          show-select
          class="elevation-1"
          no-data-text="Nincsenek menük"
          loading-text="Betöltés..."
          density="comfortable"
        >
          <!-- Date column -->
          <template #item.date="{ item }">
            <v-chip
              color="primary"
              variant="outlined"
              size="small"
            >
              {{ formatDate(item.date) }}
            </v-chip>
          </template>

          <!-- Frequency column -->
          <template #item.freq="{ item }">
            <v-chip
              :color="getFrequencyColor(item.freq)"
              variant="outlined"
              size="small"
            >
              {{ getFrequencyLabel(item.freq) }}
            </v-chip>
          </template>

          <!-- Name column -->
          <template #item.name="{ item }">
            <span class="font-weight-medium">{{ item.name }}</span>
          </template>
        </v-data-table>
      </v-card-text>

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn
          color="grey"
          variant="outlined"
          @click="cancel"
        >
          <v-icon class="me-2">
            mdi-close
          </v-icon>
          Mégse
        </v-btn>
        <v-btn
          color="primary"
          variant="elevated"
          :disabled="!selectedItems.length"
          @click="confirm"
        >
          <v-icon class="me-2">
            mdi-check
          </v-icon>
          Kiválasztás
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: "MenuSelectionDialog",
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: 'Menü kiválasztása'
    },
    getterFunc: {
      type: Function,
      required: true
    }
  },
  emits: ['update:modelValue', 'confirm'],
  data() {
    return {
      loading: false,
      menus: [],
      selectedItems: [],
      headers: [
        { title: 'ID', key: 'id', sortable: true, width: '80px' },
        { title: 'Dátum', key: 'date', sortable: true, width: '150px' },
        { title: 'Név', key: 'name', sortable: true },
        { title: 'Gyakoriság', key: 'freq', sortable: true, width: '150px' }
      ]
    }
  },
  watch: {
    modelValue(newVal) {
      if (newVal) {
        this.loadMenus();
        this.selectedItems = [];
      }
    }
  },
  methods: {
    async loadMenus() {
      try {
        this.loading = true;
        const response = await this.getterFunc();

        if (response.status === 200) {
          this.menus = response.data.data || response.data || [];
        }
      } catch (error) {
        console.error('Error loading menus:', error);
        this.menus = [];
      } finally {
        this.loading = false;
      }
    },

    formatDate(dateString) {
      if (!dateString) return '-';
      return new Date(dateString).toLocaleDateString('hu-HU', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      });
    },

    getFrequencyColor(freq) {
      const colors = {
        'daily': 'success',
        'weekly': 'info',
        'monthly': 'warning',
        'yearly': 'error'
      };
      return colors[freq] || 'grey';
    },

    getFrequencyLabel(freq) {
      const labels = {
        'daily': 'Napi',
        'weekly': 'Heti',
        'monthly': 'Havi',
        'yearly': 'Éves'
      };
      return labels[freq] || freq;
    },

    cancel() {
      this.selectedItems = [];
      this.$emit('update:modelValue', false);
    },

    confirm() {
      if (this.selectedItems.length > 0) {
        this.$emit('confirm', this.selectedItems[0]);
        this.$emit('update:modelValue', false);
      }
    }
  }
};
</script>

<style scoped>
:deep(.v-data-table__tr--selected) {
  background-color: rgba(var(--v-theme-primary), 0.1) !important;
}

:deep(.v-data-table__tr:hover) {
  background-color: rgba(var(--v-theme-on-surface), 0.04) !important;
}
</style>
