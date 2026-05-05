<template>
  <v-dialog
    :model-value="modelValue"
    max-width="600"
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

      <v-card-text class="pa-0">
        <div
          v-if="loading"
          class="d-flex justify-center pa-6"
        >
          <v-progress-circular
            indeterminate
            color="primary"
          />
        </div>

        <div
          v-else-if="menus.length === 0"
          class="pa-6 text-center text-medium-emphasis"
        >
          Nincsenek menük
        </div>

        <v-list
          v-else
          lines="two"
          select-strategy="single-leaf"
        >
          <v-list-item
            v-for="menu in menus"
            :key="menu.id"
            :value="menu"
            :active="selectedMenu && selectedMenu.id === menu.id"
            active-color="primary"
            rounded="lg"
            class="ma-1"
            @click="selectedMenu = menu"
          >
            <template #prepend>
              <v-icon :color="selectedMenu && selectedMenu.id === menu.id ? 'primary' : 'grey'">
                {{ selectedMenu && selectedMenu.id === menu.id ? 'mdi-radiobox-marked' : 'mdi-radiobox-blank' }}
              </v-icon>
            </template>
            <v-list-item-title class="font-weight-medium">
              {{ menu.name }}
            </v-list-item-title>
            <v-list-item-subtitle>
              {{ formatDateRange(menu.from_date, menu.to_date) }}
            </v-list-item-subtitle>
          </v-list-item>
        </v-list>
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
          :disabled="!selectedMenu"
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
      selectedMenu: null,
    };
  },
  watch: {
    modelValue(newVal) {
      if (newVal) {
        this.selectedMenu = null;
        this.loadMenus();
      }
    }
  },
  methods: {
    async loadMenus() {
      try {
        this.loading = true;
        this.menus = [];
        const response = await this.getterFunc();
        if (response && response.status === 200) {
          const raw = response.data?.data?.menus;
          this.menus = Array.isArray(raw) ? raw : [];
        }
      } catch (error) {
        console.error('Error loading menus:', error);
        this.menus = [];
      } finally {
        this.loading = false;
      }
    },

    formatDateRange(from, to) {
      if (!from && !to) return '';
      const fmt = (d) => d ? new Date(d).toLocaleDateString('hu-HU') : '?';
      if (from === to) return fmt(from);
      return `${fmt(from)} – ${fmt(to)}`;
    },

    cancel() {
      this.selectedMenu = null;
      this.$emit('update:modelValue', false);
    },

    confirm() {
      if (this.selectedMenu) {
        this.$emit('confirm', this.selectedMenu);
        this.$emit('update:modelValue', false);
      }
    }
  }
};
</script>

<style scoped>
:deep(.v-list-item--active) {
  background-color: rgba(var(--v-theme-primary), 0.08) !important;
}
</style>
