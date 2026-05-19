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

        <div class="d-flex gap-2 align-center">
          <!-- Unsaved size changes indicator + actions -->
          <template v-if="dirtyCount > 0 && !reorderMode">
            <v-chip
              size="small"
              color="deep-orange"
              variant="elevated"
            >
              {{ dirtyCount }} méret módosítva
            </v-chip>
            <v-btn
              color="success"
              variant="elevated"
              size="small"
              prepend-icon="mdi-content-save-all"
              @click="saveAllSizes"
            >
              Mentés
            </v-btn>
            <v-btn
              color="white"
              variant="outlined"
              size="small"
              prepend-icon="mdi-undo-variant"
              @click="discardAllSizes"
            >
              Visszaállítás
            </v-btn>
          </template>

          <!-- Selected count chip -->
          <v-chip
            v-if="selectionMode && (selectedIds.length > 0 || selectAllMode)"
            size="small"
            color="primary"
            variant="elevated"
          >
            {{ $t('bulk.selection.count_chip', { n: selectAllMode ? totalCount : selectedIds.length }) }}
          </v-chip>

          <!-- Bulk action buttons (visible when items are selected) -->
          <template v-if="selectionMode && (selectedIds.length > 0 || selectAllMode)">
            <v-btn
              color="primary"
              variant="elevated"
              size="small"
              prepend-icon="mdi-pencil-box-multiple"
              @click="showBulkEditDialog = true"
            >
              {{ $t('bulk.edit.button') }}
            </v-btn>
            <v-btn
              color="error"
              variant="elevated"
              size="small"
              prepend-icon="mdi-delete-sweep"
              @click="bulkDeleteDialog = true"
            >
              {{ $t('bulk.delete.button') }}
            </v-btn>
          </template>

          <!-- Selection Mode Toggle -->
          <v-btn
            :color="selectionMode ? 'success' : 'dark'"
            :variant="selectionMode ? 'elevated' : 'outlined'"
            :prepend-icon="selectionMode ? 'mdi-check' : 'mdi-checkbox-multiple-marked-outline'"
            :disabled="reorderMode"
            @click="toggleSelectionMode"
          >
            {{ selectionMode ? $t('bulk.selection.finish') : $t('bulk.selection.toggle') }}
          </v-btn>

          <!-- Reorder Mode Toggle -->
          <v-btn
            :color="reorderMode ? 'success' : 'dark'"
            :variant="reorderMode ? 'elevated' : 'outlined'"
            :prepend-icon="reorderMode ? 'mdi-check' : 'mdi-drag-horizontal-variant'"
            :loading="reorderLoading"
            :disabled="selectionMode"
            @click="toggleReorderMode"
          >
            {{ reorderMode ? 'Befejezés' : 'Átrendezés' }}
          </v-btn>
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
          <div class="v-data-table-header d-flex align-center pa-3 bg-secondary">
            <!-- Selection checkbox header -->
            <div
              v-if="selectionMode"
              style="width: 32px; min-width: 32px;"
              class="me-1 d-flex align-center"
              @click.stop
            >
              <v-checkbox
                :model-value="allPageSelected"
                :indeterminate="somePageSelected"
                density="compact"
                hide-details
                @update:model-value="toggleHeaderCheckbox"
              />
            </div>
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

          <!-- Select All Banner -->
          <div
            v-if="selectionMode && allPageSelected && !selectAllMode && totalCount > sortedItems.length"
            class="d-flex justify-center align-center pa-2 border-b"
          >
            <v-chip
              color="primary"
              variant="tonal"
              @click="selectAllMode = true"
            >
              {{ $t('bulk.selection.select_all_chip', { n: totalCount }) }}
            </v-chip>
          </div>
          <div
            v-if="selectionMode && selectAllMode"
            class="d-flex justify-center align-center pa-2 border-b"
          >
            <v-chip
              color="primary"
              variant="elevated"
              closable
              @click:close="clearSelection"
            >
              {{ $t('bulk.selection.all_selected', { n: totalCount }) }}
            </v-chip>
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
                  <!-- Selection Checkbox -->
                  <div
                    v-if="selectionMode"
                    style="width: 32px; min-width: 32px;"
                    class="me-1 d-flex align-center"
                    @click.stop
                  >
                    <v-checkbox
                      :model-value="selectedIds.includes(item.id)"
                      density="compact"
                      hide-details
                      @update:model-value="toggleItemSelection(item.id)"
                    />
                  </div>

                  <!-- Expand Icon -->
                  <div
                    class="me-2 d-flex align-center"
                    style="width: 32px;"
                  >
                    <v-badge
                      :model-value="dirtyItemIds.has(item.id)"
                      color="deep-orange"
                      dot
                      floating
                    >
                      <v-btn
                        :icon="expanded.has(item.id) ? 'mdi-chevron-down' : 'mdi-chevron-right'"
                        size="small"
                        variant="text"
                        density="compact"
                      />
                    </v-badge>
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
                      @click.stop=""
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
                      @click.stop=""
                    />
                    <span v-else>{{ item.description || '-' }}</span>
                  </div>

                  <!-- Category -->
                  <div
                    class="px-2 text-center col-category"
                  >
                    <v-combobox
                      v-if="item.isEditing"
                      v-model="item.category"
                      :items="categoryNames"
                      variant="outlined"
                      density="compact"
                      hide-details
                      clearable
                      @click.stop=""
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

                  <!-- Packaging Fee -->
                  <div
                    class="px-2 text-center col-packaging-fee"
                  >
                    <v-text-field
                      v-if="item.isEditing"
                      v-model.number="item.packaging_fee"
                      type="number"
                      variant="outlined"
                      density="compact"
                      hide-details
                      clearable
                      :placeholder="`${getEffectivePackagingFee(item)} (Kat.)`"
                      min="0"
                      style="min-width: 100px"
                      @click.stop=""
                    />
                    <v-chip
                      v-else-if="getEffectivePackagingFee(item) > 0"
                      size="small"
                      :color="item.packaging_fee != null ? 'warning' : 'default'"
                      variant="outlined"
                    >
                      {{ getEffectivePackagingFee(item) }} Ft
                    </v-chip>
                    <span
                      v-else
                      class="text-medium-emphasis text-caption"
                    >—</span>
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
                    :size-edits="sizeEdits"
                    @update-size="(size) => $emit('update-size', item.id, size)"
                    @cancel-size-edit="(size) => $emit('cancel-size-edit', item.id, size)"
                    @duplicate-size="(size) => $emit('duplicate-size', item.id, size)"
                    @delete-size="(size) => $emit('delete-size', item.id, size)"
                    @reorder-sizes="(sizes) => $emit('reorder-sizes', item.id, sizes)"
                    @size-field-changed="handleSizeFieldChanged"
                  />

                  <!-- Option Group Assignments -->
                  <div
                    v-if="vendorOptionGroups.length > 0 || (item.option_groups && item.option_groups.length > 0)"
                    class="pa-3 border-t option-groups-row"
                  >
                    <div class="d-flex align-center gap-2 flex-wrap">
                      <span class="text-caption font-weight-bold text-medium-emphasis me-1">
                        <v-icon size="small">mdi-tune</v-icon>
                        Opció csoportok:
                      </span>
                      <v-chip
                        v-for="group in (item.option_groups || [])"
                        :key="group.id"
                        size="small"
                        color="primary"
                        variant="tonal"
                        closable
                        @click:close="unassignGroup(item, group)"
                      >
                        {{ group.name }}
                      </v-chip>
                      <v-select
                        v-if="unassignedGroups(item).length > 0"
                        :model-value="null"
                        :items="unassignedGroups(item)"
                        item-title="name"
                        item-value="id"
                        label="Csoport hozzáadása"
                        variant="outlined"
                        density="compact"
                        hide-details
                        style="max-width: 220px"
                        @update:model-value="(gid) => { if (gid) assignGroup(item, gid) }"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </template>
          </v-virtual-scroll>
        </template>
      </v-card-text>

      <!-- Bulk Edit Dialog -->
      <BulkEditDialog
        v-model="showBulkEditDialog"
        :selected-count="selectAllMode ? totalCount : selectedIds.length"
        :menu-id="menuId"
        :vendor-id="vendorId"
        @apply="handleBulkEditApply"
      />

      <!-- Bulk Delete Confirmation Dialog -->
      <v-dialog
        v-model="bulkDeleteDialog"
        max-width="450"
      >
        <v-card>
          <v-card-title class="text-h6">
            <v-icon class="me-2 text-error">
              mdi-alert
            </v-icon>
            {{ $t('bulk.delete.dialog_title') }}
          </v-card-title>
          <v-card-text>
            {{ $t('bulk.delete.dialog_body', { n: selectAllMode ? totalCount : selectedIds.length }) }}
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn
              color="grey"
              variant="text"
              @click="bulkDeleteDialog = false"
            >
              {{ $t('bulk.delete.cancel') }}
            </v-btn>
            <v-btn
              color="error"
              variant="elevated"
              @click="executeBulkDelete"
            >
              {{ $t('bulk.delete.confirm') }}
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

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
import BulkEditDialog from './BulkEditDialog.vue';
import SizesTable from './SizesTable.vue';
import { useCategoriesStore } from '@/stores/categories';
import { useOptionGroupsStore } from '@/stores/option_groups';

export default {
  name: "ItemsDataTable",
  components: {
    BulkEditDialog,
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
    },
    vendorId: {
      type: String,
      default: null
    },
    menuId: {
      type: [Number, String],
      default: null
    },
    totalCount: {
      type: Number,
      default: 0
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
    'update-size',
    'cancel-size-edit',
    'add-size',
    'duplicate-size',
    'delete-size',
    'reorder-sizes',
    'bulk-update-sizes',
    'enter-reorder-mode',
    'exit-reorder-mode',
    'bulk-edit-items',
    'bulk-delete-items'
  ],
  setup() {
    const categoriesStore = useCategoriesStore();
    const optionGroupsStore = useOptionGroupsStore();
    return { categoriesStore, optionGroupsStore };
  },
  data() {
    return {
      sizeEdits: {},
      sortBy: 'index',
      sortOrder: 'asc',
      deleteDialog: false,
      itemToDelete: null,
      selectionMode: false,
      selectedIds: [],
      selectAllMode: false,
      showBulkEditDialog: false,
      bulkDeleteDialog: false,
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
        { title: 'Csomag. díj', key: 'packaging_fee', sortable: true, width: '130px' },
        { title: 'Sorrend', key: 'index', sortable: true, width: '120px' },
        { title: 'Műveletek', key: 'actions', sortable: false, width: '300px' }
      ],
      sortableHeaders: [
        { key: 'name', title: 'Név' },
        { key: 'description', title: 'Leírás' },
        { key: 'category', title: 'Kategória' },
        { key: 'packaging_fee', title: 'Csomag. díj' },
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

        if (this.sortBy === 'index') {
          return this.sortOrder === 'asc' ? valA - valB : valB - valA;
        }

        return this.sortOrder === 'asc'
          ? String(valA).localeCompare(String(valB))
          : String(valB).localeCompare(String(valA));
      });
    },

    allPageSelected() {
      if (this.sortedItems.length === 0) return false;
      return this.sortedItems.every(item => this.selectedIds.includes(item.id));
    },

    somePageSelected() {
      return this.sortedItems.some(item => this.selectedIds.includes(item.id)) && !this.allPageSelected;
    },

    dirtyCount() {
      return Object.keys(this.sizeEdits).length;
    },

    dirtyItemIds() {
      const ids = new Set();
      Object.values(this.sizeEdits).forEach(e => ids.add(e.itemId));
      return ids;
    },

    categoryNames() {
      return this.vendorId ? this.categoriesStore.namesForVendor(this.vendorId) : [];
    },
    vendorOptionGroups() {
      return this.vendorId ? this.optionGroupsStore.forVendor(this.vendorId) : [];
    },
  },
  watch: {
    selectionMode(newVal) {
      if (!newVal) {
        this.clearSelection();
      }
    },

    reorderMode(newVal) {
      if (newVal) {
        this.initReorderMode();
      } else {
        this.exitReorderMode();
      }
    },
    items() {
      if (this.reorderMode) {
        this.initReorderMode();
      }
      // Clear dirty edits after any server reload
      this.sizeEdits = {};
    }
  },
  mounted() {
    if (this.reorderMode) {
      this.initReorderMode();
    }
    if (this.vendorId) {
      this.optionGroupsStore.fetchByVendor(this.vendorId);
    }
  },

  beforeUnmount() {
    this.cleanupDragListeners();
  },
  methods: {
    buildBulkSelector() {
      return this.selectAllMode
        ? { select_all_menu_id: this.menuId }
        : { item_ids: [...this.selectedIds] };
    },

    handleBulkEditApply({ patch, sizePriceData }) {
      this.$emit('bulk-edit-items', { ...this.buildBulkSelector(), patch, sizePriceData });
      this.showBulkEditDialog = false;
    },

    executeBulkDelete() {
      this.$emit('bulk-delete-items', this.buildBulkSelector());
      this.bulkDeleteDialog = false;
    },

    toggleSelectionMode() {
      this.selectionMode = !this.selectionMode;
    },

    toggleItemSelection(id) {
      const idx = this.selectedIds.indexOf(id);
      if (idx === -1) {
        this.selectedIds.push(id);
      } else {
        this.selectedIds.splice(idx, 1);
      }
      this.selectAllMode = false;
    },

    toggleHeaderCheckbox() {
      if (this.allPageSelected) {
        const pageIds = new Set(this.sortedItems.map(i => i.id));
        this.selectedIds = this.selectedIds.filter(id => !pageIds.has(id));
        this.selectAllMode = false;
      } else {
        const existing = new Set(this.selectedIds);
        this.sortedItems.forEach(item => {
          if (!existing.has(item.id)) this.selectedIds.push(item.id);
        });
      }
    },

    clearSelection() {
      this.selectedIds = [];
      this.selectAllMode = false;
    },

    getEffectivePackagingFee(item) {
      if (item.packaging_fee != null) return item.packaging_fee;
      const cats = this.vendorId ? (this.categoriesStore.byVendor[this.vendorId] || []) : [];
      const cat = cats.find(c => c.name === item.category);
      return cat ? (cat.default_packaging_fee ?? 0) : 0;
    },

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
      const updatedItems = this.reorderItems.map((item, i) => ({
        ...item,
        index: i + 1
      }));
      this.$emit('reorder-items', updatedItems);
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

    handleSizeFieldChanged({ sizeId, itemId, field, value }) {
      const item = this.items.find(i => i.id === itemId);
      const size = item?.sizes.find(s => s.id === sizeId);
      if (!size) return;

      const existing = this.sizeEdits[sizeId];
      const updated = existing
        ? { ...existing, [field]: value }
        : {
            itemId,
            original: { name: size.name, price: size.price, unlimited: size.unlimited, quantity: size.quantity },
            name: size.name,
            price: size.price,
            unlimited: size.unlimited,
            quantity: size.quantity,
            [field]: value
          };

      const o = updated.original;
      const isChanged =
        updated.name !== o.name ||
        Number(updated.price) !== Number(o.price) ||
        updated.unlimited !== o.unlimited ||
        Number(updated.quantity) !== Number(o.quantity);

      if (isChanged) {
        this.sizeEdits = { ...this.sizeEdits, [sizeId]: updated };
      } else {
        const next = { ...this.sizeEdits };
        delete next[sizeId];
        this.sizeEdits = next;
      }
    },

    saveAllSizes() {
      const sizes = Object.entries(this.sizeEdits).map(([sizeId, edit]) => ({
        sizeId: Number(sizeId),
        itemId: edit.itemId,
        name: edit.name,
        price: edit.price,
        unlimited: edit.unlimited,
        quantity: edit.quantity
      }));
      this.$emit('bulk-update-sizes', sizes);
    },

    discardAllSizes() {
      this.sizeEdits = {};
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
    },

    unassignedGroups(item) {
      const assignedIds = new Set((item.option_groups || []).map(g => g.id));
      return this.vendorOptionGroups.filter(g => !assignedIds.has(g.id));
    },

    async assignGroup(item, groupId) {
      if (!groupId) return;
      const idx = (item.option_groups || []).length;
      try {
        await this.optionGroupsStore.assignToItem(item.id, groupId, idx);
        await this.optionGroupsStore.fetchByVendor(this.vendorId);
        if (!item.option_groups) item.option_groups = [];
        const group = this.vendorOptionGroups.find(g => g.id === groupId);
        if (group && !item.option_groups.find(g => g.id === groupId)) {
          item.option_groups.push(group);
        }
      } catch (e) {
        console.error('Assign failed', e);
      }
    },

    async unassignGroup(item, group) {
      try {
        await this.optionGroupsStore.unassignFromItem(item.id, group.id);
        await this.optionGroupsStore.fetchByVendor(this.vendorId);
        if (item.option_groups) {
          item.option_groups = item.option_groups.filter(g => g.id !== group.id);
        }
      } catch (e) {
        console.error('Unassign failed', e);
      }
    },
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

.col-packaging-fee {
  width: 130px;
  min-width: 130px;
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
