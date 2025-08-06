<template>
  <v-container
    fluid
    class="pa-4"
  >
    <v-card
      elevation="2"
      class="mx-auto"
    >
      <v-card-title class="d-flex justify-space-between align-center bg-primary text-white">
        <h2 class="text-h6 font-weight-bold">
          <v-icon class="me-2">
            mdi-food-variant
          </v-icon>
          Ételek listája
        </h2>

        <div class="d-flex gap-2">
          <!-- Reorder Mode Toggle -->
          <v-btn
            :color="reorderMode ? 'success' : 'dark'"
            :variant="reorderMode ? 'elevated' : 'outlined'"
            :prepend-icon="reorderMode ? 'mdi-check' : 'mdi-drag-horizontal-variant'"
            :loading="reorderLoading"
            @click="toggleReorderMode"
          >
            {{ reorderMode ? 'Befejezés' : 'Átrendezés' }}
          </v-btn>

          <!-- Sort Menu (only in normal mode) -->
          <v-menu v-if="!reorderMode">
            <template #activator="{ props }">
              <v-btn
                v-bind="props"
                color="dark"
                variant="outlined"
                prepend-icon="mdi-sort"
              >
                Rendezés
              </v-btn>
            </template>

            <v-list>
              <v-list-item
                v-for="header in sortableHeaders"
                :key="header.key"
                @click="toggleSort(header.key)"
              >
                <v-list-item-title>
                  {{ header.title }}
                  <v-icon
                    v-if="sortBy === header.key"
                    :class="sortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down'"
                    size="small"
                    class="ms-2"
                  />
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </div>
      </v-card-title>

      <!-- Reorder Mode Notice -->
      <v-alert
        v-if="reorderMode"
        type="info"
        variant="tonal"
        class="ma-4 mb-0"
        icon="mdi-information"
      >
        <v-alert-title>Átrendezési mód</v-alert-title>
        Húzza és ejtse az elemeket az újrarendezéshez. Az expandált sorok le vannak zárva ebben a módban.
      </v-alert>

      <v-card-text class="pa-0">
        <!-- Virtual Scroller for Reorder Mode -->
        <template v-if="reorderMode">
          <v-virtual-scroll
            :items="reorderItems"
            :item-height="72"
            height="600"
            class="reorder-virtual-scroll"
          >
            <template #default="{ item }">
              <div
                :key="item.id"
                :data-item-id="item.id"
                class="reorder-item d-flex align-center pa-3"
                :class="{
                  'dragging': draggingItemId === item.id
                }"
              >
                <!-- Drag Handle -->
                <v-icon
                  class="drag-handle me-3 text-medium-emphasis"
                  size="small"
                >
                  mdi-drag-vertical
                </v-icon>

                <!-- Index -->
                <div
                  class="me-4"
                  style="min-width: 40px;"
                >
                  <v-chip
                    size="small"
                    color="primary"
                    variant="outlined"
                  >
                    {{ item.index }}
                  </v-chip>
                </div>

                <!-- Content -->
                <div class="flex-grow-1">
                  <div class="font-weight-medium">
                    {{ item.name }}
                  </div>
                  <div class="text-caption text-medium-emphasis">
                    {{ item.description || 'Nincs leírás' }} •
                    <v-chip
                      size="x-small"
                      color="primary"
                      variant="outlined"
                    >
                      {{ item.category }}
                    </v-chip>
                  </div>
                </div>

                <!-- Sizes Count -->
                <div class="me-3 text-caption text-medium-emphasis">
                  {{ item.sizes?.length || 0 }} méret
                </div>
              </div>
            </template>
          </v-virtual-scroll>
        </template>

        <!-- Virtual Scrolled Data Table for Normal Mode -->
        <template v-else>
          <!-- Table Header -->
          <div class="v-data-table-header d-flex align-center pa-3 bg-grey-lighten-4">
            <div
              class="me-2"
              style="width: 24px;"
            />
            <div
              v-for="header in headers"
              :key="header.key"
              :style="{ width: header.width || 'auto' }"
              class="font-weight-bold text-body-2 text-medium-emphasis px-2"
              :class="(header.align || 'text-left') + ' col-' + header.key"
            >
              <div
                v-if="header.sortable"
                class="d-flex align-center cursor-pointer"
                @click="toggleSort(header.key)"
              >
                {{ header.title }}
                <v-icon
                  v-if="sortBy === header.key"
                  size="small"
                  class="ms-1"
                >
                  {{ sortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down' }}
                </v-icon>
              </div>
              <span v-else>{{ header.title }}</span>
            </div>
          </div>

          <!-- Virtual Scrolled Table Body -->
          <v-virtual-scroll
            :items="sortedItems"
            :item-height="itemHeight"
            height="600"
            class="virtual-table-scroll"
          >
            <template #default="{ item }">
              <div class="virtual-table-row">
                <!-- Main Row -->
                <div
                  :key="item.id"
                  class="d-flex align-center pa-2 border-b virtual-row"
                  :class="{
                    'row-expanded': expanded.has(item.id),
                    'row-hover': true
                  }"
                  @click="toggleExpanded(item.id)"
                >
                  <!-- Expand Icon -->
                  <div
                    class="me-2"
                    style="width: 24px;"
                  >
                    <v-btn
                      :icon="expanded.has(item.id) ? 'mdi-chevron-down' : 'mdi-chevron-right'"
                      size="small"
                      variant="text"
                      density="compact"
                    />
                  </div>

                  <!-- ID -->
                  <div
                    class="px-2 text-body-2 col-id"
                  >
                    {{ item.id }}
                  </div>

                  <!-- Name -->
                  <div
                    class="px-2 col-name"
                  >
                    <v-text-field
                      v-if="item.isEditing"
                      v-model="item.name"
                      variant="outlined"
                      density="compact"
                      hide-details
                    />
                    <span
                      v-else
                      class="font-weight-medium"
                    >{{ item.name }}</span>
                  </div>

                  <!-- Description -->
                  <div
                    class="px-2 col-description"
                  >
                    <v-text-field
                      v-if="item.isEditing"
                      v-model="item.description"
                      variant="outlined"
                      density="compact"
                      hide-details
                    />
                    <span v-else>{{ item.description || '-' }}</span>
                  </div>

                  <!-- Category -->
                  <div
                    class="px-2 text-center col-category"
                  >
                    <v-text-field
                      v-if="item.isEditing"
                      v-model="item.category"
                      variant="outlined"
                      density="compact"
                      hide-details
                    />
                    <v-chip
                      v-else
                      color="primary"
                      variant="outlined"
                      size="small"
                    >
                      {{ item.category }}
                    </v-chip>
                  </div>

                  <!-- Index -->
                  <div
                    class="px-2 text-center col-index"
                  >
                    <v-chip
                      size="small"
                      color="secondary"
                      variant="outlined"
                    >
                      {{ item.index }}
                    </v-chip>
                  </div>

                  <!-- Actions -->
                  <div
                    class="px-2 col-actions"
                  >
                    <div class="d-flex gap-1">
                      <!-- Edit/Save/Cancel buttons -->
                      <template v-if="!item.isEditing">
                        <v-tooltip text="Szerkesztés">
                          <template #activator="{ props }">
                            <v-btn
                              v-bind="props"
                              icon="mdi-pencil"
                              size="small"
                              variant="text"
                              color="primary"
                              @click.stop="$emit('edit-item', item)"
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
                              size="small"
                              variant="text"
                              color="success"
                              @click.stop="$emit('update-item', item)"
                            />
                          </template>
                        </v-tooltip>

                        <v-tooltip text="Mégse">
                          <template #activator="{ props }">
                            <v-btn
                              v-bind="props"
                              icon="mdi-close"
                              size="small"
                              variant="text"
                              color="error"
                              @click.stop="$emit('cancel-edit', item)"
                            />
                          </template>
                        </v-tooltip>
                      </template>

                      <!-- Other action buttons -->
                      <v-tooltip text="Duplikálás">
                        <template #activator="{ props }">
                          <v-btn
                            v-bind="props"
                            icon="mdi-content-duplicate"
                            size="small"
                            variant="text"
                            color="info"
                            @click.stop="$emit('duplicate-item', item)"
                          />
                        </template>
                      </v-tooltip>

                      <v-tooltip text="Méret hozzáadása">
                        <template #activator="{ props }">
                          <v-btn
                            v-bind="props"
                            icon="mdi-plus-circle"
                            size="small"
                            variant="text"
                            color="success"
                            @click.stop="$emit('add-size', item.id)"
                          />
                        </template>
                      </v-tooltip>

                      <v-tooltip text="Áthelyezés">
                        <template #activator="{ props }">
                          <v-btn
                            v-bind="props"
                            icon="mdi-file-move"
                            size="small"
                            variant="text"
                            color="warning"
                            @click.stop="$emit('move-item', item)"
                          />
                        </template>
                      </v-tooltip>

                      <v-tooltip text="Másolás">
                        <template #activator="{ props }">
                          <v-btn
                            v-bind="props"
                            icon="mdi-content-copy"
                            size="small"
                            variant="text"
                            color="info"
                            @click.stop="$emit('copy-item', item)"
                          />
                        </template>
                      </v-tooltip>

                      <v-tooltip text="Törlés">
                        <template #activator="{ props }">
                          <v-btn
                            v-bind="props"
                            icon="mdi-delete"
                            size="small"
                            variant="text"
                            color="error"
                            @click.stop="confirmDelete(item)"
                          />
                        </template>
                      </v-tooltip>
                    </div>
                  </div>
                </div>

                <!-- Expanded Content -->
                <div
                  v-if="expanded.has(item.id)"
                  class="expanded-content pa-0"
                >
                  <SizesTable
                    :item-id="item.id"
                    :sizes="item.sizes"
                    @edit-size="(size) => $emit('edit-size', item.id, size)"
                    @update-size="(size) => $emit('update-size', item.id, size)"
                    @cancel-size-edit="(size) => $emit('cancel-size-edit', item.id, size)"
                    @duplicate-size="(size) => $emit('duplicate-size', item.id, size)"
                    @delete-size="(size) => $emit('delete-size', item.id, size)"
                    @reorder-sizes="(sizes) => $emit('reorder-sizes', item.id, sizes)"
                  />
                </div>
              </div>
            </template>
          </v-virtual-scroll>
        </template>
      </v-card-text>

      <!-- Delete Confirmation Dialog -->
      <v-dialog
        v-model="deleteDialog"
        max-width="400"
      >
        <v-card>
          <v-card-title class="text-h6">
            <v-icon class="me-2 text-error">
              mdi-alert
            </v-icon>
            Törlés megerősítése
          </v-card-title>

          <v-card-text>
            Biztosan törölni szeretné a(z) <strong>{{ itemToDelete?.name }}</strong> ételt?
            Ez a művelet nem vonható vissza.
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
              @click="deleteItem"
            >
              Törlés
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-card>
  </v-container>
</template>

<script>
import SizesTable from './SizesTable.vue';

export default {
  name: "ItemsDataTable",
  components: {
    SizesTable
  },
  props: {
    items: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    sortable: {
      type: Boolean,
      default: true
    }
  },
  emits: [
    'edit-item',
    'update-item',
    'cancel-edit',
    'duplicate-item',
    'move-item',
    'copy-item',
    'delete-item',
    'reorder-items',
    'edit-size',
    'update-size',
    'cancel-size-edit',
    'add-size',
    'duplicate-size',
    'delete-size',
    'reorder-sizes',
    'enter-reorder-mode',
    'exit-reorder-mode',
    'bulk-update-indices'
  ],
  data() {
    return {
      sortBy: 'index',
      sortOrder: 'asc',
      deleteDialog: false,
      itemToDelete: null,
      reorderMode: false,
      reorderLoading: false,
      reorderItems: [],
      expanded: new Set(),
      draggingItemId: null,
      dragInsertBefore: true,
      dragOverItemId: null,
      itemHeight: 52,
      headers: [
        { title: 'ID', key: 'id', sortable: false, width: '80px' },
        { title: 'Név', key: 'name', sortable: true },
        { title: 'Leírás', key: 'description', sortable: true },
        { title: 'Kategória', key: 'category', sortable: true },
        { title: 'Sorrend', key: 'index', sortable: true, width: '120px' },
        { title: 'Műveletek', key: 'actions', sortable: false, width: '300px' }
      ],
      sortableHeaders: [
        { key: 'name', title: 'Név' },
        { key: 'description', title: 'Leírás' },
        { key: 'category', title: 'Kategória' },
        { key: 'index', title: 'Sorrend' }
      ]
    }
  },
  computed: {
    sortedItems() {
      if (!this.sortBy) return this.items;

      return [...this.items].sort((a, b) => {
        const valA = a[this.sortBy];
        const valB = b[this.sortBy];

        // Special numeric sort for 'index'
        if (this.sortBy === 'index') {
          return this.sortOrder === 'asc'
            ? valA - valB
            : valB - valA;
        }

        // Default string comparison
        return this.sortOrder === 'asc'
          ? String(valA).localeCompare(String(valB))
          : String(valB).localeCompare(String(valA));
      });
    }
  },
  watch: {
    reorderMode(newVal) {
      if (newVal) {
        this.initReorderMode();
      } else {
        this.exitReorderMode();
      }
    }
  },
  mounted() {
    if (this.reorderMode) {
      this.initReorderMode();
    }
  },

  beforeUnmount() {
    this.cleanupDragListeners();
  },
  methods: {
    rowProps(data) {
      return {
        'data-item-id': data.item.id
      };
    },

    toggleExpanded(itemId) {
      if (this.expanded.has(itemId)) {
        this.expanded.delete(itemId);
      } else {
        this.expanded.add(itemId);
      }
      this.$forceUpdate(); // Force reactivity for Set changes
    },

    toggleSort(key) {
      if (this.sortBy === key) {
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortBy = key;
        this.sortOrder = 'asc';
      }
    },

    async toggleReorderMode() {
      this.reorderLoading = true;

      try {
        if (!this.reorderMode) {
          // Enter reorder mode
          this.$emit('enter-reorder-mode');
          this.reorderMode = true;
        } else {
          // Exit reorder mode and save changes
          await this.saveReorderChanges();
          this.$emit('exit-reorder-mode');
          this.reorderMode = false;
        }
      } finally {
        this.reorderLoading = false;
      }
    },

    async saveReorderChanges() {
      // Update indices based on current order
      this.$emit('reorder-items', this.reorderItems);
      const updatedItems = this.reorderItems.map((item, index) => ({
        ...item,
        index: index + 1
      }));

      // Emit bulk update event
      this.$emit('bulk-update-indices', updatedItems);
    },

    initReorderMode() {
      // Close all expanded rows
      this.expanded = new Set();

      // Sort items by index for reordering
      this.reorderItems = [...this.items].sort((a, b) => a.index - b.index);

      this.$nextTick(() => {
        this.initDragAndDropForReorder();
      });
    },

    exitReorderMode() {
      this.reorderItems = [];
      this.draggingItemId = null;
      this.dragOverItemId = null;
      this.cleanupDragListeners();
    },

    initDragAndDropForReorder() {
      this.$nextTick(() => {
        const scrollContainer = this.$el.querySelector('.v-virtual-scroll__container');
        if (scrollContainer) {
          scrollContainer.addEventListener('mousedown', this.handleMouseDown);
        }
      });
    },

    cleanupDragListeners() {
      const scrollContainer = this.$el?.querySelector('.v-virtual-scroll__container');
      if (scrollContainer) {
        scrollContainer.removeEventListener('mousedown', this.handleMouseDown);
      }

      // Clean up document listeners
      document.removeEventListener('mousemove', this.handleMouseMove);
      document.removeEventListener('mouseup', this.handleMouseUp);
    },

    handleMouseDown(e) {
      const dragHandle = e.target.closest('.drag-handle');
      if (!dragHandle) return;

      const reorderItem = dragHandle.closest('.reorder-item');
      if (!reorderItem) return;

      e.preventDefault();

      const itemId = reorderItem.dataset.itemId;
      this.draggingItemId = itemId;

      // Store initial mouse position
      this.dragStartY = e.clientY;
      this.dragCurrentY = e.clientY;

      // Add visual feedback
      reorderItem.style.opacity = '0.8';
      reorderItem.style.transform = 'scale(1.02)';
      reorderItem.style.zIndex = '1000';
      reorderItem.style.backgroundColor = 'rgba(var(--v-theme-primary), 0.1)';

      // Add document listeners for mouse move and up
      document.addEventListener('mousemove', this.handleMouseMove);
      document.addEventListener('mouseup', this.handleMouseUp);
    },

    handleMouseMove(e) {
      if (!this.draggingItemId) return;

      e.preventDefault();
      this.dragCurrentY = e.clientY;

      // Find the item we're hovering over
      const elements = document.elementsFromPoint(e.clientX, e.clientY);
      const targetItem = elements.find(el => el.classList.contains('reorder-item'));

      if (targetItem && targetItem.dataset.itemId !== this.draggingItemId) {
        const rect = targetItem.getBoundingClientRect();
        const offsetY = e.clientY - rect.top;
        this.dragInsertBefore = offsetY < rect.height / 2;

        this.dragOverItemId = targetItem.dataset.itemId;

        // Add visual feedback to target
        document.querySelectorAll('.reorder-item').forEach(item => {
          item.style.boxShadow = '';

          if (item.dataset.itemId === this.dragOverItemId) {
            if (this.dragInsertBefore) {
              item.style.boxShadow = '0 -3px 0 0 rgb(var(--v-theme-primary))';
            } else {
              item.style.boxShadow = '0 3px 0 0 rgb(var(--v-theme-primary))';
            }
          }
        });
      }
    },

    handleMouseUp(e) {
      if (!this.draggingItemId) return;

      e.preventDefault();

      // Reset visual feedback for all items
      document.querySelectorAll('.reorder-item').forEach(item => {
        item.style.opacity = '';
        item.style.transform = '';
        item.style.zIndex = '';
        item.style.backgroundColor = '';
        item.style.boxShadow = '';
      });

      // Perform the reorder if we have a valid target
      if (this.dragOverItemId && this.dragOverItemId !== this.draggingItemId) {
        this.performReorder(this.draggingItemId, this.dragOverItemId, this.dragInsertBefore);
      }

      // Clean up
      this.draggingItemId = null;
      this.dragOverItemId = null;

      // Remove document listeners
      document.removeEventListener('mousemove', this.handleMouseMove);
      document.removeEventListener('mouseup', this.handleMouseUp);
    },

    performReorder(draggedItemId, targetItemId, before) {
      const draggedIndex = this.reorderItems.findIndex(item => String(item.id) === draggedItemId);
      const targetIndex = this.reorderItems.findIndex(item => String(item.id) === targetItemId);

      if (draggedIndex === -1 || targetIndex === -1 || draggedIndex === targetIndex) return;

      const newItems = [...this.reorderItems];
      const [draggedItem] = newItems.splice(draggedIndex, 1);

      // felfele mozgatás before
      // lefele mozgatás after
      let insertIndex = targetIndex;
      // lefele mozgatás before
      if (before && draggedIndex < targetIndex) {
        insertIndex -= 1;
      }
      // felfel mozgatás after
      if (!before && draggedIndex > targetIndex) {
        insertIndex += 1;
      }

      newItems.splice(insertIndex, 0, draggedItem);
      this.reorderItems = newItems;

      // Force reactivity update
      this.$forceUpdate();
    },

    confirmDelete(item) {
      this.itemToDelete = item;
      this.deleteDialog = true;
    },

    deleteItem() {
      if (this.itemToDelete) {
        this.$emit('delete-item', this.itemToDelete);
        this.deleteDialog = false;
        this.itemToDelete = null;
      }
    }
  }
};
</script>

<style scoped>
.drag-handle {
  cursor: grab;
  transition: color 0.2s ease;
}

.drag-handle:hover {
  color: var(--v-theme-primary) !important;
}

.drag-handle:active {
  cursor: grabbing;
}

.v-card {
  border-radius: 12px !important;
}

.reorder-item {
  transition: all 0.2s ease;
  border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  user-select: none;
}

.reorder-item:hover {
  background-color: rgba(var(--v-theme-on-surface), 0.04);
}

.reorder-item.dragging {
  opacity: 0.8;
  transform: scale(1.02);
  z-index: 1000;
  background-color: rgba(var(--v-theme-primary), 0.1);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.reorder-virtual-scroll {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

:deep(.v-data-table__tr--clickable:hover) {
  background-color: rgba(var(--v-theme-on-surface), 0.04);
}

.v-data-table-header {
  position: sticky;
  top: 0;
  z-index: 2;
  border-bottom: 2px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.virtual-table-scroll {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.virtual-table-row {
  min-height: 52px;
}

.virtual-row {
  transition: background-color 0.2s ease;
  cursor: pointer;
}

.virtual-row:hover {
  background-color: rgba(var(--v-theme-on-surface), 0.04);
}

.row-expanded {
  background-color: rgba(var(--v-theme-primary), 0.05);
}

.expanded-content {
  background-color: rgba(var(--v-theme-surface), 1);
  border-left: 3px solid rgb(var(--v-theme-primary));
}

.cursor-pointer {
  cursor: pointer;
}

.col-id {
  width: 80px;
  min-width: 80px;
}

.col-name {
  flex: 1;
  min-width: 200px;
}

.col-description {
  flex: 1;
  min-width: 200px;
}

.col-category {
  width: 150px;
  min-width: 150px;
}

.col-index {
  width: 120px;
  min-width: 120px;
}

.col-actions {
  width: 300px;
  min-width: 300px;
}
</style>
