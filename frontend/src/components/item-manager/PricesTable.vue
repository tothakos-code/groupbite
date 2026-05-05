<template>
  <v-card
    elevation="2"
    class="mx-auto"
  >
    <v-card-title class="d-flex justify-space-between align-center bg-primary text-white flex-wrap gap-2 pa-4">
      <div class="d-flex align-center">
        <v-icon class="me-2">
          mdi-tag-multiple
        </v-icon>
        <span class="text-h6 font-weight-bold">Árak kezelése</span>
      </div>
      <div class="d-flex gap-2 align-center">
        <v-chip
          v-if="dirtyCount > 0"
          color="warning"
          variant="elevated"
          size="small"
        >
          {{ dirtyCount }} módosítás
        </v-chip>
        <v-btn
          :disabled="dirtyCount === 0"
          color="success"
          variant="elevated"
          :loading="loading"
          prepend-icon="mdi-content-save-all"
          @click="saveAll"
        >
          Mentés
        </v-btn>
        <v-btn
          :disabled="dirtyCount === 0"
          color="white"
          variant="outlined"
          prepend-icon="mdi-undo-variant"
          @click="discardAll"
        >
          Visszaállítás
        </v-btn>
      </div>
    </v-card-title>

    <v-alert
      type="info"
      variant="tonal"
      class="ma-4 mb-2"
      icon="mdi-cursor-pointer"
      density="compact"
    >
      Kattintson egy értékre a szerkesztéshez. Enter vagy kattintás máshova elfogadja, Escape visszavonja. A Mentés gomb az összes változtatást egyszerre rögzíti.
    </v-alert>

    <v-card-text class="pa-3 pb-1">
      <v-text-field
        v-model="localSearch"
        placeholder="Szűrés étel vagy méret neve alapján..."
        variant="outlined"
        density="compact"
        prepend-inner-icon="mdi-magnify"
        clearable
        hide-details
      />
    </v-card-text>

    <v-card-text class="pa-0">
      <v-data-table
        :headers="headers"
        :items="filteredRows"
        :group-by="groupBy"
        density="compact"
        no-data-text="Nincsenek méretek"
        hide-default-footer
        items-per-page="-1"
        item-value="id"
      >
        <template #group-header="{ item, columns, toggleGroup, isGroupOpen }">
          <tr class="group-header-row">
            <td
              :colspan="columns.length"
              class="py-2 px-4"
            >
              <v-btn
                :icon="isGroupOpen(item) ? 'mdi-chevron-down' : 'mdi-chevron-right'"
                variant="text"
                density="compact"
                size="small"
                class="me-1"
                @click="toggleGroup(item)"
              />
              <strong>{{ item.value }}</strong>
              <v-chip
                size="x-small"
                class="ms-2"
                color="primary"
                variant="outlined"
              >
                {{ item.items.length }} méret
              </v-chip>
            </td>
          </tr>
        </template>

        <template #item.status="{ item }">
          <v-tooltip
            v-if="item.dirty"
            text="Nem mentett változás"
            location="right"
          >
            <template #activator="{ props }">
              <v-icon
                v-bind="props"
                color="warning"
                size="small"
              >
                mdi-circle-medium
              </v-icon>
            </template>
          </v-tooltip>
        </template>

        <template #item.sizeName="{ item }">
          <div
            class="editable-cell"
            @click="startEdit(item, 'sizeName')"
          >
            <v-text-field
              v-if="item.editing === 'sizeName'"
              v-model="item.sizeName"
              variant="outlined"
              density="compact"
              hide-details
              autofocus
              class="editable-input"
              @blur="commitEdit(item)"
              @keyup.enter="commitEdit(item)"
              @keyup.escape="cancelEdit(item, 'sizeName')"
              @click.stop
            />
            <span
              v-else
              class="editable-value"
              :class="{ 'dirty-value': item.dirty }"
            >
              {{ item.sizeName }}
              <v-icon
                size="x-small"
                class="edit-hint ms-1"
              >
                mdi-pencil-outline
              </v-icon>
            </span>
          </div>
        </template>

        <template #item.price="{ item }">
          <div
            class="editable-cell"
            @click="startEdit(item, 'price')"
          >
            <v-text-field
              v-if="item.editing === 'price'"
              v-model.number="item.price"
              variant="outlined"
              density="compact"
              hide-details
              type="number"
              min="0"
              suffix="Ft"
              autofocus
              class="editable-input price-input"
              @blur="commitEdit(item)"
              @keyup.enter="commitEdit(item)"
              @keyup.escape="cancelEdit(item, 'price')"
              @click.stop
            />
            <span
              v-else
              class="editable-value font-weight-medium"
              :class="{ 'dirty-value': item.dirty }"
            >
              {{ formatPrice(item.price) }}
              <v-icon
                size="x-small"
                class="edit-hint ms-1"
              >
                mdi-pencil-outline
              </v-icon>
            </span>
          </div>
        </template>

        <template #item.unlimited="{ item }">
          <v-checkbox
            v-model="item.unlimited"
            hide-details
            density="compact"
            color="primary"
            @update:model-value="markDirty(item)"
          />
        </template>

        <template #item.quantity="{ item }">
          <div
            class="editable-cell"
            :class="{ 'non-editable': item.unlimited }"
            @click="!item.unlimited && startEdit(item, 'quantity')"
          >
            <v-text-field
              v-if="item.editing === 'quantity' && !item.unlimited"
              v-model.number="item.quantity"
              variant="outlined"
              density="compact"
              hide-details
              type="number"
              min="0"
              autofocus
              class="editable-input"
              @blur="commitEdit(item)"
              @keyup.enter="commitEdit(item)"
              @keyup.escape="cancelEdit(item, 'quantity')"
              @click.stop
            />
            <v-chip
              v-else-if="item.unlimited"
              color="success"
              size="x-small"
              variant="outlined"
            >
              <v-icon start>
                mdi-infinity
              </v-icon>
              Végtelen
            </v-chip>
            <span
              v-else
              class="editable-value"
              :class="{ 'dirty-value': item.dirty }"
            >
              {{ item.quantity }}
              <v-icon
                size="x-small"
                class="edit-hint ms-1"
              >
                mdi-pencil-outline
              </v-icon>
            </span>
          </div>
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: "PricesTable",
  props: {
    items: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['save-sizes'],
  data() {
    return {
      flatRows: [],
      localSearch: '',
      groupBy: [{ key: 'itemName' }],
      headers: [
        { title: '', key: 'status', sortable: false, width: '32px' },
        { title: 'Méret neve', key: 'sizeName', sortable: true },
        { title: 'Ár', key: 'price', sortable: true, width: '170px' },
        { title: 'Végtelen', key: 'unlimited', sortable: false, width: '100px' },
        { title: 'Mennyiség', key: 'quantity', sortable: false, width: '140px' }
      ]
    };
  },
  computed: {
    dirtyCount() {
      return this.flatRows.filter(r => r.dirty).length;
    },
    filteredRows() {
      if (!this.localSearch) return this.flatRows;
      const q = this.localSearch.toLowerCase();
      return this.flatRows.filter(r =>
        r.itemName.toLowerCase().includes(q) ||
        r.sizeName.toLowerCase().includes(q)
      );
    }
  },
  watch: {
    items: {
      immediate: true,
      handler(newItems) {
        this.buildFlatRows(newItems);
      }
    }
  },
  methods: {
    buildFlatRows(items) {
      this.flatRows = items.flatMap(item =>
        (item.sizes || []).map(size => ({
          id: `${item.id}-${size.id}`,
          itemId: item.id,
          itemName: item.name,
          sizeId: size.id,
          sizeName: size.name,
          price: size.price,
          unlimited: size.unlimited,
          quantity: size.quantity,
          dirty: false,
          editing: null,
          original: {
            sizeName: size.name,
            price: size.price,
            unlimited: size.unlimited,
            quantity: size.quantity
          }
        }))
      );
    },

    startEdit(row, field) {
      row.editing = field;
    },

    commitEdit(row) {
      row.editing = null;
      this.markDirty(row);
    },

    cancelEdit(row, field) {
      row[field] = row.original[field];
      row.editing = null;
    },

    markDirty(row) {
      const o = row.original;
      row.dirty =
        row.sizeName !== o.sizeName ||
        Number(row.price) !== Number(o.price) ||
        row.unlimited !== o.unlimited ||
        Number(row.quantity) !== Number(o.quantity);
    },

    discardAll() {
      this.flatRows.forEach(row => {
        row.sizeName = row.original.sizeName;
        row.price = row.original.price;
        row.unlimited = row.original.unlimited;
        row.quantity = row.original.quantity;
        row.dirty = false;
        row.editing = null;
      });
    },

    saveAll() {
      const dirty = this.flatRows.filter(r => r.dirty);
      if (!dirty.length) return;
      this.$emit('save-sizes', dirty.map(r => ({
        sizeId: r.sizeId,
        itemId: r.itemId,
        name: r.sizeName,
        price: r.price,
        unlimited: r.unlimited,
        quantity: r.quantity
      })));
    },

    formatPrice(price) {
      return new Intl.NumberFormat('hu-HU', {
        style: 'currency',
        currency: 'HUF',
        minimumFractionDigits: 0
      }).format(price || 0);
    }
  }
};
</script>

<style scoped>
.editable-cell {
  cursor: pointer;
  min-height: 32px;
  display: flex;
  align-items: center;
}

.non-editable {
  cursor: default;
}

.editable-value {
  padding: 4px 6px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  transition: background-color 0.15s;
}

.editable-value:hover {
  background-color: rgba(var(--v-theme-primary), 0.08);
}

.edit-hint {
  opacity: 0;
  transition: opacity 0.15s;
}

.editable-value:hover .edit-hint {
  opacity: 0.4;
}

.dirty-value {
  color: rgb(var(--v-theme-warning));
}

.editable-input {
  min-width: 100px;
}

.price-input {
  min-width: 130px;
}

.group-header-row {
  background-color: rgba(var(--v-theme-secondary), 0.15) !important;
}

:deep(.v-data-table__tr:hover) {
  background-color: rgba(var(--v-theme-primary), 0.03) !important;
}
</style>
