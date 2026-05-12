<template>
  <v-container
    fluid
    class="pa-4"
    max-width="1000"
  >
    <v-row
      align="center"
      no-gutters
      class="mb-4"
    >
      <v-col>
        <h2 class="text-h5 font-weight-bold">
          <v-icon class="me-2">
            mdi-tag-multiple
          </v-icon>
          Menü ajánlatok
        </h2>
      </v-col>
    </v-row>

    <!-- Create bundle form -->
    <v-card
      elevation="2"
      class="mb-5"
    >
      <v-card-title class="bg-primary text-white text-h6 pa-3">
        <v-icon class="me-2">
          mdi-plus
        </v-icon>
        Új ajánlat
      </v-card-title>
      <v-card-text class="pa-4">
        <v-row dense>
          <v-col
            cols="12"
            sm="5"
          >
            <v-text-field
              v-model="newBundle.name"
              label="Ajánlat neve"
              variant="outlined"
              density="comfortable"
              hide-details
            />
          </v-col>
          <v-col
            cols="12"
            sm="5"
          >
            <v-text-field
              v-model="newBundle.description"
              label="Leírás (opcionális)"
              variant="outlined"
              density="comfortable"
              hide-details
            />
          </v-col>
          <v-col
            cols="12"
            sm="2"
            class="d-flex align-center"
          >
            <v-btn
              color="primary"
              variant="elevated"
              :loading="saving"
              :disabled="!newBundle.name"
              @click="createBundle"
            >
              <v-icon start>
                mdi-plus
              </v-icon>
              Hozzáadás
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Bundle list -->
    <v-progress-linear
      v-if="loading"
      indeterminate
      color="primary"
      class="mb-4"
    />

    <div
      v-if="bundles.length === 0 && !loading"
      class="text-center py-10 text-medium-emphasis"
    >
      <v-icon
        size="48"
        class="mb-2"
      >
        mdi-tag-off
      </v-icon>
      <p>Még nincsenek menü ajánlatok. Hozz létre egyet!</p>
    </div>

    <v-expansion-panels
      v-model="openPanels"
      multiple
      variant="accordion"
    >
      <v-expansion-panel
        v-for="bundle in bundles"
        :key="bundle.id"
        class="mb-2"
      >
        <v-expansion-panel-title>
          <div class="d-flex align-center gap-2 flex-grow-1">
            <span class="font-weight-medium">{{ bundle.name }}</span>
            <span
              v-if="bundle.description"
              class="text-caption text-medium-emphasis"
            >
              {{ bundle.description }}
            </span>
            <v-chip
              size="x-small"
              color="secondary"
              variant="tonal"
            >
              {{ bundle.slots.length }} slot
            </v-chip>
          </div>
          <template #actions>
            <div
              class="d-flex align-center me-2"
              @click.stop
            >
              <v-btn
                icon="mdi-pencil"
                size="small"
                variant="text"
                color="primary"
                @click.stop="startEditBundle(bundle)"
              />
              <v-btn
                icon="mdi-delete"
                size="small"
                variant="text"
                color="error"
                @click.stop="deleteBundle(bundle)"
              />
              <v-icon class="ms-2">
                mdi-chevron-down
              </v-icon>
            </div>
          </template>
        </v-expansion-panel-title>

        <v-expansion-panel-text class="pa-0">
          <!-- Inline edit form -->
          <div
            v-if="editingBundleId === bundle.id"
            class="px-4 pt-5 pb-4 border-b"
          >
            <v-row dense>
              <v-col
                cols="12"
                sm="5"
              >
                <v-text-field
                  v-model="editBundleForm.name"
                  label="Név"
                  variant="outlined"
                  density="compact"
                  hide-details
                />
              </v-col>
              <v-col
                cols="12"
                sm="5"
              >
                <v-text-field
                  v-model="editBundleForm.description"
                  label="Leírás"
                  variant="outlined"
                  density="compact"
                  hide-details
                />
              </v-col>
              <v-col
                cols="12"
                sm="2"
                class="d-flex gap-1 align-center"
              >
                <v-btn
                  color="primary"
                  size="small"
                  variant="elevated"
                  @click="saveBundle(bundle.id)"
                >
                  Mentés
                </v-btn>
                <v-btn
                  size="small"
                  variant="text"
                  @click="editingBundleId = null"
                >
                  Mégse
                </v-btn>
              </v-col>
            </v-row>
          </div>

          <!-- Slots list -->
          <v-list
            density="compact"
            class="pa-0"
          >
            <v-list-item
              v-for="slot in bundle.slots"
              :key="slot.id"
              class="border-b"
            >
              <template #prepend>
                <v-icon
                  size="small"
                  color="secondary"
                >
                  mdi-circle-small
                </v-icon>
              </template>

              <template v-if="editingSlotId === slot.id">
                <div class="d-flex align-center gap-2 flex-wrap pt-5 pb-2">
                  <v-select
                    v-model="editSlotForm.match_type"
                    :items="matchTypeOptions"
                    item-title="label"
                    item-value="value"
                    label="Típus"
                    variant="outlined"
                    density="compact"
                    hide-details
                    style="max-width: 160px"
                  />
                  <v-select
                    v-if="editSlotForm.match_type === 'category'"
                    v-model="editSlotForm.category_id"
                    :items="vendorCategories"
                    item-title="name"
                    item-value="id"
                    label="Kategória"
                    variant="outlined"
                    density="compact"
                    hide-details
                    clearable
                    style="min-width: 160px; max-width: 240px"
                  />
                  <v-select
                    v-else-if="editSlotForm.match_type === 'item'"
                    v-model="editSlotForm.menu_item_id"
                    :items="vendorItems"
                    item-title="name"
                    item-value="id"
                    label="Étel"
                    variant="outlined"
                    density="compact"
                    hide-details
                    clearable
                    style="min-width: 160px; max-width: 240px"
                  />
                  <v-text-field
                    v-model.number="editSlotForm.price_override"
                    label="Fix ár (Ft)"
                    type="number"
                    variant="outlined"
                    density="compact"
                    hide-details
                    clearable
                    style="max-width: 130px"
                    @click:clear="editSlotForm.price_override = null"
                  />
                  <v-text-field
                    v-model.number="editSlotForm.price_delta"
                    label="Kedvezmény (Ft)"
                    placeholder="200"
                    type="number"
                    variant="outlined"
                    density="compact"
                    hide-details
                    clearable
                    style="max-width: 150px"
                    @click:clear="editSlotForm.price_delta = null"
                  />
                  <v-btn
                    color="primary"
                    size="small"
                    variant="elevated"
                    :disabled="!isEditSlotValid()"
                    @click="saveSlot(bundle.id, slot.id)"
                  >
                    Mentés
                  </v-btn>
                  <v-btn
                    size="small"
                    variant="text"
                    @click="editingSlotId = null"
                  >
                    Mégse
                  </v-btn>
                </div>
              </template>

              <template v-else>
                <v-list-item-title class="text-body-2">
                  <v-chip
                    size="x-small"
                    color="primary"
                    variant="outlined"
                    class="me-1"
                  >
                    {{ slot.match_type === 'category' ? 'Kategória' : 'Étel' }}
                  </v-chip>
                  {{ slotLabel(slot) }}
                  <span
                    v-if="slot.price_override != null"
                    class="text-caption text-medium-emphasis ms-2"
                  >
                    Fix: {{ slot.price_override }} Ft
                  </span>
                  <span
                    v-if="slot.price_delta != null"
                    class="text-caption text-medium-emphasis ms-2"
                  >
                    Kedvezmény: {{ slot.price_delta }} Ft
                  </span>
                </v-list-item-title>
              </template>

              <template #append>
                <div
                  v-if="editingSlotId !== slot.id"
                  class="d-flex"
                >
                  <v-btn
                    icon="mdi-pencil"
                    size="x-small"
                    variant="text"
                    color="primary"
                    @click="startEditSlot(slot)"
                  />
                  <v-btn
                    icon="mdi-delete"
                    size="x-small"
                    variant="text"
                    color="error"
                    @click="deleteSlot(bundle, slot)"
                  />
                </div>
              </template>
            </v-list-item>

            <!-- Add slot row -->
            <v-list-item class="px-3 pt-5 pb-3">
              <div class="d-flex align-center gap-2 flex-wrap">
                <v-select
                  v-model="newSlots[bundle.id].match_type"
                  :items="matchTypeOptions"
                  item-title="label"
                  item-value="value"
                  label="Típus"
                  variant="outlined"
                  density="compact"
                  hide-details
                  style="max-width: 160px"
                />
                <v-select
                  v-if="newSlots[bundle.id].match_type === 'category'"
                  v-model="newSlots[bundle.id].category_id"
                  :items="vendorCategories"
                  item-title="name"
                  item-value="id"
                  label="Kategória"
                  variant="outlined"
                  density="compact"
                  hide-details
                  clearable
                  style="min-width: 160px; max-width: 240px"
                />
                <v-select
                  v-else-if="newSlots[bundle.id].match_type === 'item'"
                  v-model="newSlots[bundle.id].menu_item_id"
                  :items="vendorItems"
                  item-title="name"
                  item-value="id"
                  label="Étel"
                  variant="outlined"
                  density="compact"
                  hide-details
                  clearable
                  style="min-width: 160px; max-width: 240px"
                />
                <v-text-field
                  v-model.number="newSlots[bundle.id].price_override"
                  label="Fix ár (Ft)"
                  type="number"
                  variant="outlined"
                  density="compact"
                  hide-details
                  clearable
                  style="max-width: 130px"
                  @click:clear="newSlots[bundle.id].price_override = null"
                />
                <v-text-field
                  v-model.number="newSlots[bundle.id].price_delta"
                  label="Kedvezmény (Ft)"
                  placeholder="200"
                  type="number"
                  variant="outlined"
                  density="compact"
                  hide-details
                  clearable
                  style="max-width: 150px"
                  @click:clear="newSlots[bundle.id].price_delta = null"
                />
                <v-btn
                  color="primary"
                  size="small"
                  variant="elevated"
                  :disabled="!isNewSlotValid(bundle.id)"
                  @click="addSlot(bundle.id)"
                >
                  <v-icon start>
                    mdi-plus
                  </v-icon>
                  Slot hozzáadása
                </v-btn>
              </div>
            </v-list-item>
          </v-list>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>

    <!-- Snackbar -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="3000"
    >
      {{ snackbar.text }}
    </v-snackbar>
  </v-container>
</template>

<script>
import { useBundlesStore } from '@/stores/bundles'
import { useCategoriesStore } from '@/stores/categories'
import { useVendorStore } from '@/stores/vendor'

export default {
  name: 'VendorBundleManager',
  setup() {
    const bundlesStore = useBundlesStore()
    const categoriesStore = useCategoriesStore()
    const vendorStore = useVendorStore()
    return { bundlesStore, categoriesStore, vendorStore }
  },
  data() {
    return {
      loading: false,
      saving: false,
      openPanels: [],
      editingBundleId: null,
      editingSlotId: null,
      editBundleForm: { name: '', description: '' },
      editSlotForm: { slot_index: 0, match_type: 'category', category_id: null, menu_item_id: null, price_override: null, price_delta: null },
      newBundle: { name: '', description: '' },
      newSlots: {},
      vendorMenuItems: [],
      snackbar: { show: false, text: '', color: 'success' },
      matchTypeOptions: [
        { label: 'Kategória', value: 'category' },
        { label: 'Étel', value: 'item' },
      ],
    }
  },
  computed: {
    vendorId() {
      return this.$route.params.id
    },
    bundles() {
      return this.bundlesStore.forVendor(this.vendorId)
    },
    vendorCategories() {
      return this.categoriesStore.byVendor[this.vendorId] || []
    },
    vendorItems() {
      return this.vendorMenuItems
    },
  },
  watch: {
    bundles(val) {
      for (const b of val) {
        if (!this.newSlots[b.id]) {
          this.newSlots[b.id] = this.emptySlot(b.slots.length)
        }
      }
    },
  },
  async mounted() {
    this.loading = true
    await Promise.all([
      this.bundlesStore.fetchByVendor(this.vendorId),
      this.categoriesStore.fetchByVendor(this.vendorId),
      this.loadMenuItems(),
    ])
    this.loading = false
  },
  methods: {
    showSnackbar(text, color = 'success') {
      this.snackbar = { show: true, text, color }
    },

    emptySlot(index = 0) {
      return { slot_index: index, match_type: 'category', category_id: null, menu_item_id: null, price_override: null, price_delta: null }
    },

    async loadMenuItems() {
      try {
        const response = await this.vendorStore.fetchMenus(this.vendorId)
        if (response?.status === 200) {
          const menus = response.data.data?.menus || []
          const all = menus.flatMap(m => m.items || [])
          const seen = new Set()
          this.vendorMenuItems = all.filter(item => {
            if (seen.has(item.id)) return false
            seen.add(item.id)
            return true
          })
        }
      } catch (e) {
        console.error('Failed to load menu items', e)
      }
    },

    slotLabel(slot) {
      if (slot.match_type === 'category') {
        const cat = this.vendorCategories.find(c => c.id === slot.category_id)
        return cat ? cat.name : `Kategória #${slot.category_id}`
      }
      const item = this.vendorMenuItems.find(i => i.id === slot.menu_item_id)
      return item ? item.name : `Étel #${slot.menu_item_id}`
    },

    async createBundle() {
      this.saving = true
      try {
        await this.bundlesStore.createBundle(this.vendorId, { ...this.newBundle })
        this.newBundle = { name: '', description: '' }
        this.showSnackbar('Ajánlat létrehozva')
      } catch {
        this.showSnackbar('Hiba történt', 'error')
      } finally {
        this.saving = false
      }
    },

    startEditBundle(bundle) {
      this.editingBundleId = bundle.id
      this.editBundleForm = { name: bundle.name, description: bundle.description || '' }
    },

    async saveBundle(bundleId) {
      try {
        await this.bundlesStore.updateBundle(this.vendorId, bundleId, { ...this.editBundleForm })
        this.editingBundleId = null
        this.showSnackbar('Ajánlat mentve')
      } catch {
        this.showSnackbar('Hiba történt', 'error')
      }
    },

    async deleteBundle(bundle) {
      try {
        await this.bundlesStore.deleteBundle(this.vendorId, bundle.id)
        this.showSnackbar('Ajánlat törölve')
      } catch (e) {
        const msg = e?.response?.data?.error || 'Hiba történt'
        this.showSnackbar(msg, 'error')
      }
    },

    async addSlot(bundleId) {
      const form = this.newSlots[bundleId]
      const slotIndex = (this.bundles.find(b => b.id === bundleId)?.slots?.length ?? 0)
      const payload = {
        slot_index: slotIndex,
        match_type: form.match_type,
        category_id: form.match_type === 'category' ? (form.category_id ?? null) : null,
        menu_item_id: form.match_type === 'item' ? (form.menu_item_id ?? null) : null,
        price_override: form.price_override != null && form.price_override !== '' ? Number(form.price_override) : null,
        price_delta: form.price_delta != null && form.price_delta !== '' ? Number(form.price_delta) : null,
      }
      try {
        await this.bundlesStore.addSlot(this.vendorId, bundleId, payload)
        this.newSlots[bundleId] = this.emptySlot(slotIndex + 1)
        this.showSnackbar('Slot hozzáadva')
      } catch {
        this.showSnackbar('Hiba történt', 'error')
      }
    },

    startEditSlot(slot) {
      this.editingSlotId = slot.id
      this.editSlotForm = {
        slot_index: slot.slot_index,
        match_type: slot.match_type,
        category_id: slot.category_id,
        menu_item_id: slot.menu_item_id,
        price_override: slot.price_override,
        price_delta: slot.price_delta,
      }
    },

    async saveSlot(bundleId, slotId) {
      const payload = {
        slot_index: this.editSlotForm.slot_index,
        match_type: this.editSlotForm.match_type,
        category_id: this.editSlotForm.match_type === 'category' ? (this.editSlotForm.category_id ?? null) : null,
        menu_item_id: this.editSlotForm.match_type === 'item' ? (this.editSlotForm.menu_item_id ?? null) : null,
        price_override: this.editSlotForm.price_override != null && this.editSlotForm.price_override !== '' ? Number(this.editSlotForm.price_override) : null,
        price_delta: this.editSlotForm.price_delta != null && this.editSlotForm.price_delta !== '' ? Number(this.editSlotForm.price_delta) : null,
      }
      try {
        await this.bundlesStore.updateSlot(this.vendorId, bundleId, slotId, payload)
        this.editingSlotId = null
        this.showSnackbar('Slot mentve')
      } catch {
        this.showSnackbar('Hiba történt', 'error')
      }
    },

    async deleteSlot(bundle, slot) {
      try {
        await this.bundlesStore.deleteSlot(this.vendorId, bundle.id, slot.id)
        this.showSnackbar('Slot törölve')
      } catch (e) {
        const msg = e?.response?.data?.error || 'Hiba történt'
        this.showSnackbar(msg, 'error')
      }
    },

    isNewSlotValid(bundleId) {
      const form = this.newSlots[bundleId]
      if (!form?.match_type) return false
      if (form.match_type === 'category' && !form.category_id) return false
      if (form.match_type === 'item' && !form.menu_item_id) return false
      return true
    },

    isEditSlotValid() {
      const form = this.editSlotForm
      if (!form.match_type) return false
      if (form.match_type === 'category' && !form.category_id) return false
      if (form.match_type === 'item' && !form.menu_item_id) return false
      return true
    },
  },
}
</script>

<style scoped>
.gap-2 { gap: 8px; }
</style>
