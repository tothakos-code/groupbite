<template>
  <v-card
    variant="flat"
    class="ma-4"
  >
    <v-card-title class="text-subtitle-1 bg-secondary">
      <v-icon class="me-2">
        mdi-resize
      </v-icon>
      Méretek kezelése
    </v-card-title>

    <v-card-text class="pa-0">
      <v-data-table
        :headers="headers"
        :items="mergedSizes"
        :sort-by="[{ key: 'index', order: 'asc' }]"
        item-key="id"
        class="elevation-0 bg-header"
        density="compact"
        no-data-text="Nincsenek méretek"
        hide-default-footer
      >
        <!-- Index / drag handle -->
        <template #item.index="{ item }">
          <div class="d-flex align-center">
            <v-icon
              v-if="item.id !== -1"
              class="drag-handle me-2 text-medium-emphasis"
              size="small"
              style="cursor: grab;"
            >
              mdi-drag-vertical
            </v-icon>
            <span>{{ item.index }}</span>
          </div>
        </template>

        <!-- Name -->
        <template #item.name="{ item }">
          <!-- New unsaved size: plain input -->
          <v-text-field
            v-if="item.id === -1"
            v-model="item.name"
            variant="outlined"
            density="compact"
            hide-details
            placeholder="Méret neve"
          />
          <!-- Existing: click-to-edit -->
          <div
            v-else
            class="editable-cell"
            @click="startEdit(item, 'name')"
          >
            <v-text-field
              v-if="isEditing(item.id, 'name')"
              v-model="editingValue"
              variant="outlined"
              density="compact"
              hide-details
              autofocus
              class="editable-input"
              @blur="commitEdit(item)"
              @keyup.enter="commitEdit(item)"
              @keyup.escape="cancelEdit()"
              @click.stop
            />
            <span
              v-else
              class="editable-value font-weight-medium"
              :class="{ 'dirty-value': isDirty(item.id) }"
            >
              {{ item.name }}
              <v-icon
                size="x-small"
                class="edit-hint ms-1"
              >
                mdi-pencil-outline
              </v-icon>
            </span>
          </div>
        </template>

        <!-- Price -->
        <template #item.price="{ item }">
          <v-text-field
            v-if="item.id === -1"
            v-model.number="item.price"
            variant="outlined"
            density="compact"
            hide-details
            type="number"
            min="0"
            suffix="Ft"
          />
          <div
            v-else
            class="editable-cell"
            @click="startEdit(item, 'price')"
          >
            <v-text-field
              v-if="isEditing(item.id, 'price')"
              v-model.number="editingValue"
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
              @keyup.escape="cancelEdit()"
              @click.stop
            />
            <span
              v-else
              class="editable-value font-weight-medium"
              :class="{ 'dirty-value': isDirty(item.id) }"
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

        <!-- Unlimited -->
        <template #item.unlimited="{ item }">
          <v-checkbox
            :model-value="item.unlimited"
            hide-details
            density="compact"
            color="primary"
            @update:model-value="(val) => item.id !== -1
              ? $emit('size-field-changed', { sizeId: item.id, itemId, field: 'unlimited', value: val })
              : (item.unlimited = val)"
          />
        </template>

        <!-- Quantity -->
        <template #item.quantity="{ item }">
          <v-text-field
            v-if="item.id === -1 && !item.unlimited"
            v-model.number="item.quantity"
            variant="outlined"
            density="compact"
            hide-details
            type="number"
            min="0"
            placeholder="Mennyiség"
          />
          <div
            v-else-if="item.id !== -1"
            class="editable-cell"
            :class="{ 'non-editable': item.unlimited }"
            @click="!item.unlimited && startEdit(item, 'quantity')"
          >
            <v-text-field
              v-if="isEditing(item.id, 'quantity') && !item.unlimited"
              v-model.number="editingValue"
              variant="outlined"
              density="compact"
              hide-details
              type="number"
              min="0"
              autofocus
              class="editable-input"
              @blur="commitEdit(item)"
              @keyup.enter="commitEdit(item)"
              @keyup.escape="cancelEdit()"
              @click.stop
            />
            <v-chip
              v-else-if="item.unlimited"
              color="success"
              size="small"
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
              :class="{ 'dirty-value': isDirty(item.id) }"
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
          <v-chip
            v-else
            color="success"
            size="small"
            variant="outlined"
          >
            <v-icon start>
              mdi-infinity
            </v-icon>
            Végtelen
          </v-chip>
        </template>

        <!-- Actions -->
        <template #item.actions="{ item }">
          <div class="d-flex gap-1">
            <template v-if="item.id === -1">
              <v-tooltip text="Mentés">
                <template #activator="{ props }">
                  <v-btn
                    v-bind="props"
                    icon="mdi-check"
                    size="x-small"
                    variant="text"
                    color="success"
                    @click="$emit('update-size', item)"
                  />
                </template>
              </v-tooltip>
              <v-tooltip text="Mégse">
                <template #activator="{ props }">
                  <v-btn
                    v-bind="props"
                    icon="mdi-close"
                    size="x-small"
                    variant="text"
                    color="error"
                    @click="$emit('cancel-size-edit', item)"
                  />
                </template>
              </v-tooltip>
            </template>
            <template v-else>
              <v-tooltip text="Duplikálás">
                <template #activator="{ props }">
                  <v-btn
                    v-bind="props"
                    icon="mdi-content-duplicate"
                    size="x-small"
                    variant="text"
                    color="info"
                    @click="$emit('duplicate-size', item)"
                  />
                </template>
              </v-tooltip>
              <v-tooltip text="Törlés">
                <template #activator="{ props }">
                  <v-btn
                    v-bind="props"
                    icon="mdi-delete"
                    size="x-small"
                    variant="text"
                    color="error"
                    @click="confirmDelete(item)"
                  />
                </template>
              </v-tooltip>
            </template>
          </div>
        </template>
      </v-data-table>
    </v-card-text>

    <!-- Delete Confirmation Dialog -->
    <v-dialog
      v-model="deleteDialog"
      max-width="350"
    >
      <v-card>
        <v-card-title class="text-h6">
          <v-icon class="me-2 text-error">
            mdi-alert
          </v-icon>
          Méret törlése
        </v-card-title>
        <v-card-text>
          Biztosan törölni szeretné a(z) <strong>{{ sizeToDelete?.name }}</strong> méretet?
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            color="grey"
            variant="text"
            @click="deleteDialog = false"
          >
            Mégse
          </v-btn>
          <v-btn
            color="error"
            variant="elevated"
            @click="deleteSize"
          >
            Törlés
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
export default {
  name: "SizesTable",
  props: {
    itemId: {
      type: Number,
      required: true
    },
    sizes: {
      type: Array,
      default: () => []
    },
    sizeEdits: {
      type: Object,
      default: () => ({})
    }
  },
  emits: [
    'update-size',
    'cancel-size-edit',
    'duplicate-size',
    'delete-size',
    'reorder-sizes',
    'size-field-changed'
  ],
  data() {
    return {
      editingCell: null,  // { sizeId, field }
      editingValue: null,
      deleteDialog: false,
      sizeToDelete: null,
      headers: [
        { title: 'Sorrend', key: 'index', sortable: false, width: '100px' },
        { title: 'Méret', key: 'name', sortable: false },
        { title: 'Ár', key: 'price', sortable: false, width: '150px' },
        { title: 'Végtelen', key: 'unlimited', sortable: false, width: '100px' },
        { title: 'Mennyiség', key: 'quantity', sortable: false, width: '140px' },
        { title: 'Műveletek', key: 'actions', sortable: false, width: '100px' }
      ]
    };
  },
  computed: {
    mergedSizes() {
      return this.sizes.map(size => {
        const edit = this.sizeEdits[size.id];
        if (!edit) return size;
        return {
          ...size,
          name: edit.name,
          price: edit.price,
          unlimited: edit.unlimited,
          quantity: edit.quantity
        };
      });
    }
  },
  mounted() {
    this.initDragAndDrop();
  },
  updated() {
    this.initDragAndDrop();
  },
  methods: {
    isEditing(sizeId, field) {
      return this.editingCell?.sizeId === sizeId && this.editingCell.field === field;
    },

    isDirty(sizeId) {
      return !!this.sizeEdits[sizeId];
    },

    startEdit(size, field) {
      this.editingCell = { sizeId: size.id, field };
      // Start from the committed value (edit or original)
      this.editingValue = this.sizeEdits[size.id]?.[field] ?? size[field];
    },

    commitEdit(size) {
      if (!this.editingCell) return;
      const { field } = this.editingCell;
      this.$emit('size-field-changed', {
        sizeId: size.id,
        itemId: this.itemId,
        field,
        value: this.editingValue
      });
      this.editingCell = null;
      this.editingValue = null;
    },

    cancelEdit() {
      this.editingCell = null;
      this.editingValue = null;
    },

    formatPrice(price) {
      return new Intl.NumberFormat('hu-HU', {
        style: 'currency',
        currency: 'HUF',
        minimumFractionDigits: 0
      }).format(price || 0);
    },

    confirmDelete(size) {
      this.sizeToDelete = size;
      this.deleteDialog = true;
    },

    deleteSize() {
      if (this.sizeToDelete) {
        this.$emit('delete-size', this.sizeToDelete);
        this.deleteDialog = false;
        this.sizeToDelete = null;
      }
    },

    initDragAndDrop() {
      this.$nextTick(() => {
        const tableBody = this.$el.querySelector('tbody');
        if (!tableBody) return;
        this.cleanupSortable();
        this.initSortable(tableBody);
      });
    },

    cleanupSortable() {
      if (this.sortableCleanup) {
        this.sortableCleanup();
        this.sortableCleanup = null;
      }
    },

    initSortable(container) {
      let draggedElement = null;
      let placeholder = null;
      const eventHandlers = new Map();

      const rows = container.querySelectorAll('tr');
      rows.forEach(row => {
        const dragHandle = row.querySelector('.drag-handle');
        if (!dragHandle) return;

        const mouseDownHandler = (e) => {
          e.preventDefault();
          container.querySelectorAll('.drag-placeholder').forEach(p => p.remove());
          draggedElement = row;
          placeholder = row.cloneNode(true);
          placeholder.style.opacity = '0.5';
          placeholder.style.backgroundColor = '#f5f5f5';
          placeholder.classList.add('drag-placeholder');
          row.style.opacity = '0.8';
          row.style.transform = 'scale(1.02)';
          row.style.zIndex = '1000';
          document.addEventListener('mousemove', onMouseMove);
          document.addEventListener('mouseup', onMouseUp);
        };

        dragHandle.addEventListener('mousedown', mouseDownHandler);
        eventHandlers.set(dragHandle, mouseDownHandler);
      });

      const onMouseMove = (e) => {
        if (!draggedElement) return;
        const afterElement = this.getDragAfterElement(container, e.clientY);
        if (afterElement == null) {
          container.appendChild(placeholder);
        } else {
          container.insertBefore(placeholder, afterElement);
        }
      };

      const cleanup = () => {
        if (placeholder?.parentNode) placeholder.remove();
        if (draggedElement) {
          draggedElement.style.opacity = '';
          draggedElement.style.transform = '';
          draggedElement.style.zIndex = '';
        }
        draggedElement = null;
        placeholder = null;
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
      };

      const onMouseUp = () => {
        if (!draggedElement || !placeholder) { cleanup(); return; }
        placeholder.parentNode.insertBefore(draggedElement, placeholder);
        placeholder.remove();

        const newOrder = Array.from(container.querySelectorAll('tr:not(.drag-placeholder)'))
          .map((row, index) => {
            const sizeId = parseInt(row.dataset.sizeId);
            const size = this.mergedSizes.find(s => s.id === sizeId);
            return size ? { ...size, index } : null;
          })
          .filter(Boolean);

        this.$emit('reorder-sizes', newOrder);
        cleanup();
      };

      this.sortableCleanup = () => {
        eventHandlers.forEach((handler, el) => el.removeEventListener('mousedown', handler));
        eventHandlers.clear();
        container.querySelectorAll('.drag-placeholder').forEach(p => p.remove());
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
      };
    },

    getDragAfterElement(container, y) {
      const els = [...container.querySelectorAll('tr:not(.dragging):not(.drag-placeholder)')];
      return els.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        return offset < 0 && offset > closest.offset ? { offset, element: child } : closest;
      }, { offset: Number.NEGATIVE_INFINITY }).element;
    },

    beforeDestroy() {
      this.cleanupSortable();
    }
  }
};
</script>

<style scoped>
.drag-handle:hover {
  color: var(--v-theme-primary) !important;
  cursor: grab;
}

.drag-handle:active {
  cursor: grabbing;
}

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
  color: #E65100;
  font-weight: 600;
}

.editable-input {
  min-width: 90px;
}

.price-input {
  min-width: 120px;
}

:deep(.v-data-table) {
  background-color: #fafafa;
}

:deep(.v-data-table__tr:hover) {
  background-color: rgba(var(--v-theme-primary), 0.04) !important;
}
</style>
