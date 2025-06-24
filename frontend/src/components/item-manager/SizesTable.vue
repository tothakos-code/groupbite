<template>
  <v-card
    variant="flat"
    class="ma-4"
  >
    <v-card-title class="text-subtitle-1 bg-surface-variant">
      <v-icon class="me-2">
        mdi-resize
      </v-icon>
      Méretek kezelése
    </v-card-title>

    <v-card-text class="pa-0">
      <v-data-table
        :headers="headers"
        :items="sizes"
        :sort-by="[{ key: 'index', order: 'asc' }]"
        item-key="id"
        class="elevation-0"
        density="compact"
        no-data-text="Nincsenek méretek"
        hide-default-footer
      >
        <!-- Index column with drag handle -->
        <template #item.index="{ item }">
          <div class="d-flex align-center">
            <v-icon
              class="drag-handle me-2 text-medium-emphasis"
              size="small"
              style="cursor: grab;"
            >
              mdi-drag-vertical
            </v-icon>
            <span>{{ item.index }}</span>
          </div>
        </template>

        <!-- Name column -->
        <template #item.name="{ item }">
          <v-text-field
            v-if="item.isEditing"
            v-model="item.name"
            variant="outlined"
            density="compact"
            hide-details
            placeholder="Méret neve"
          />
          <span
            v-else
            class="font-weight-medium"
          >{{ item.name }}</span>
        </template>

        <!-- Price column -->
        <template #item.price="{ item }">
          <v-text-field
            v-if="item.isEditing"
            v-model.number="item.price"
            variant="outlined"
            density="compact"
            hide-details
            type="number"
            min="0"
            step="0.01"
            suffix="Ft"
          />
          <span
            v-else
            class="font-weight-medium"
          >{{ formatPrice(item.price) }}</span>
        </template>

        <!-- Unlimited column -->
        <template #item.unlimited="{ item }">
          <v-checkbox
            v-model="item.unlimited"
            :readonly="!item.isEditing"
            hide-details
            density="compact"
            color="primary"
          />
        </template>

        <!-- Quantity column -->
        <template #item.quantity="{ item }">
          <v-text-field
            v-if="item.isEditing && !item.unlimited"
            v-model.number="item.quantity"
            variant="outlined"
            density="compact"
            hide-details
            type="number"
            min="0"
            placeholder="Mennyiség"
          />
          <span
            v-else-if="!item.unlimited"
            class="font-weight-medium"
          >
            {{ item.quantity }}
          </span>
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

        <!-- Actions column -->
        <template #item.actions="{ item }">
          <div class="d-flex gap-1">
            <!-- Edit/Save/Cancel buttons -->
            <template v-if="!item.isEditing">
              <v-tooltip text="Szerkesztés">
                <template #activator="{ props }">
                  <v-btn
                    v-bind="props"
                    icon="mdi-pencil"
                    size="x-small"
                    variant="text"
                    color="primary"
                    @click="$emit('edit-size', item)"
                  />
                </template>
              </v-tooltip>
            </template>

            <template v-else>
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

            <!-- Duplicate button -->
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

            <!-- Delete button -->
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
    }
  },
  emits: [
    'edit-size',
    'update-size',
    'cancel-size-edit',
    'duplicate-size',
    'delete-size',
    'reorder-sizes'
  ],
  data() {
    return {
      deleteDialog: false,
      sizeToDelete: null,
      headers: [
        { title: 'Sorrend', key: 'index', sortable: false, width: '100px' },
        { title: 'Méret', key: 'name', sortable: false },
        { title: 'Ár', key: 'price', sortable: false, width: '120px' },
        { title: 'Végtelen', key: 'unlimited', sortable: false, width: '100px' },
        { title: 'Mennyiség', key: 'quantity', sortable: false, width: '120px' },
        { title: 'Műveletek', key: 'actions', sortable: false, width: '180px' }
      ]
    }
  },
  mounted() {
    this.initDragAndDrop();
  },
  updated() {
    this.initDragAndDrop();
  },
  methods: {
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

        // Clean up existing sortable before initializing new one
        this.cleanupSortable();
        this.initSortable(tableBody);
      });
    },

    // Add this method to store cleanup functions
    cleanupSortable() {
      if (this.sortableCleanup) {
        this.sortableCleanup();
        this.sortableCleanup = null;
      }
    },

    initSortable(container) {
      let draggedElement = null;
      let placeholder = null;
      const eventHandlers = new Map(); // Store event handlers for cleanup

      const rows = container.querySelectorAll('tr');

      rows.forEach(row => {
        const dragHandle = row.querySelector('.drag-handle');
        if (!dragHandle) return;

        const mouseDownHandler = (e) => {
          e.preventDefault();

          // Clean up any existing placeholders in the DOM
          container.querySelectorAll('.drag-placeholder').forEach(p => p.remove());

          draggedElement = row;

          // Create placeholder
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
        // Store the handler for cleanup
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
        // Remove placeholder from DOM if it exists
        if (placeholder && placeholder.parentNode) {
          placeholder.remove();
        }

        // Reset dragged element styles
        if (draggedElement) {
          draggedElement.style.opacity = '';
          draggedElement.style.transform = '';
          draggedElement.style.zIndex = '';
        }

        // Reset variables
        draggedElement = null;
        placeholder = null;

        // Remove event listeners
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
      };

      const onMouseUp = () => {
        if (!draggedElement || !placeholder) {
          cleanup();
          return;
        }

        // Replace placeholder with dragged element
        placeholder.parentNode.insertBefore(draggedElement, placeholder);
        placeholder.remove();

        // Get new order and emit reorder event
        const newOrder = Array.from(container.querySelectorAll('tr:not(.drag-placeholder)')).map((row, index) => {
          const sizeId = parseInt(row.dataset.sizeId);
          const size = this.sizes.find(s => s.id === sizeId);
          if (size) {
            return { ...size, index };
          }
          return null;
        }).filter(Boolean);

        this.$emit('reorder-sizes', newOrder);

        cleanup();
      };

      // Store cleanup function for this sortable instance
      this.sortableCleanup = () => {
        // Remove all event listeners
        eventHandlers.forEach((handler, element) => {
          element.removeEventListener('mousedown', handler);
        });
        eventHandlers.clear();

        // Clean up any remaining placeholders
        container.querySelectorAll('.drag-placeholder').forEach(p => p.remove());

        // Remove document event listeners if they exist
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
      };
    },

    getDragAfterElement(container, y) {
      // Exclude both dragging elements and placeholders
      const draggableElements = [...container.querySelectorAll('tr:not(.dragging):not(.drag-placeholder)')];

      return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;

        if (offset < 0 && offset > closest.offset) {
          return { offset: offset, element: child };
        } else {
          return closest;
        }
      }, { offset: Number.NEGATIVE_INFINITY }).element;
    },

    // Add this to component's beforeDestroy/unmounted lifecycle
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

:deep(.v-data-table) {
  background-color: #fafafa;
}

:deep(.v-data-table__tr:hover) {
  background-color: rgba(var(--v-theme-primary), 0.04) !important;
}
</style>
