<template>
  <v-dialog
    :model-value="modelValue"
    max-width="520"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <v-card>
      <v-card-title class="text-h6 bg-primary text-white pa-4">
        {{ $t('bulk.edit.dialog_title', { n: selectedCount }) }}
      </v-card-title>

      <v-card-text class="pt-4">
        <!-- Item fields section -->
        <div class="text-overline text-medium-emphasis mb-1">
          {{ $t('bulk.edit.section_item_data') }}
        </div>
        <v-divider class="mb-4" />

        <v-combobox
          v-model="selectedCategoryId"
          :items="categories"
          item-title="name"
          item-value="id"
          :label="$t('bulk.edit.category_label')"
          clearable
          density="compact"
          hide-details="auto"
          class="mb-3"
          @update:model-value="touch('category_id')"
        />

        <v-text-field
          v-model.number="packagingFee"
          type="number"
          :label="$t('bulk.edit.packaging_fee_label')"
          clearable
          density="compact"
          hide-details="auto"
          class="mb-3"
          min="0"
          @update:model-value="touch('packaging_fee')"
        />

        <v-text-field
          v-model="description"
          :label="$t('bulk.edit.description_label')"
          clearable
          density="compact"
          hide-details="auto"
          class="mb-5"
          @update:model-value="touch('description')"
        />

        <!-- Size prices section -->
        <div class="text-overline text-medium-emphasis mb-1">
          {{ $t('bulk.edit.section_size_prices') }}
        </div>
        <v-divider class="mb-3" />

        <v-radio-group
          v-model="priceMode"
          density="compact"
          hide-details
          class="mb-3"
        >
          <v-radio
            :label="$t('bulk.edit.price_mode_none')"
            value="none"
          />
          <v-radio
            :label="$t('bulk.edit.price_mode_set')"
            value="set"
          />
          <v-radio
            :label="$t('bulk.edit.price_mode_adjust_fixed')"
            value="adjust_fixed"
          />
          <v-radio
            :label="$t('bulk.edit.price_mode_adjust_percent')"
            value="adjust_percent"
          />
        </v-radio-group>

        <v-text-field
          v-if="priceMode !== 'none'"
          v-model.number="priceValue"
          type="number"
          :label="priceValueLabel"
          density="compact"
          hide-details="auto"
        />
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn
          variant="text"
          @click="$emit('update:modelValue', false)"
        >
          {{ $t('bulk.edit.cancel') }}
        </v-btn>
        <v-btn
          color="primary"
          variant="elevated"
          :disabled="applyDisabled"
          @click="applyEdits"
        >
          {{ $t('bulk.edit.apply') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { useCategoriesStore } from '@/stores/categories';

export default {
  name: 'BulkEditDialog',

  props: {
    modelValue: { type: Boolean, required: true },
    selectedCount: { type: Number, default: 0 },
    menuId: { type: [Number, String], default: null },
    vendorId: { type: String, default: null }
  },

  emits: ['update:modelValue', 'apply'],

  setup() {
    const categoriesStore = useCategoriesStore();
    return { categoriesStore };
  },

  data() {
    return {
      selectedCategoryId: null,
      packagingFee: null,
      description: null,
      priceMode: 'none',
      priceValue: 0,
      touched: []
    };
  },

  computed: {
    categories() {
      return this.vendorId ? (this.categoriesStore.byVendor[this.vendorId] || []) : [];
    },

    applyDisabled() {
      return this.touched.length === 0 && this.priceMode === 'none';
    },

    priceValueLabel() {
      if (this.priceMode === 'set') return this.$t('bulk.edit.price_value_set');
      if (this.priceMode === 'adjust_fixed') return this.$t('bulk.edit.price_value_adjust_fixed');
      if (this.priceMode === 'adjust_percent') return this.$t('bulk.edit.price_value_adjust_percent');
      return '';
    }
  },

  watch: {
    modelValue(val) {
      if (val) this.resetForm();
    }
  },

  methods: {
    touch(field) {
      if (!this.touched.includes(field)) {
        this.touched.push(field);
      }
    },

    resetForm() {
      this.selectedCategoryId = null;
      this.packagingFee = null;
      this.description = null;
      this.priceMode = 'none';
      this.priceValue = 0;
      this.touched = [];
    },

    applyEdits() {
      const patch = {};

      if (this.touched.includes('category_id')) {
        const cat = this.selectedCategoryId;
        patch.category_id = typeof cat === 'number'
          ? cat
          : (cat != null && typeof cat === 'object' ? cat.id : null);
      }
      if (this.touched.includes('packaging_fee')) {
        patch.packaging_fee = this.packagingFee != null && this.packagingFee !== ''
          ? Number(this.packagingFee)
          : null;
      }
      if (this.touched.includes('description')) {
        patch.description = this.description ?? null;
      }

      const sizePriceData = this.priceMode !== 'none'
        ? { mode: this.priceMode, value: Number(this.priceValue) }
        : null;

      this.$emit('apply', { patch, sizePriceData });
    }
  }
};
</script>
