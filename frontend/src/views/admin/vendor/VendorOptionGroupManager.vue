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
            mdi-tune
          </v-icon>
          Opció csoportok
        </h2>
      </v-col>
    </v-row>

    <!-- Create group form -->
    <v-card
      elevation="2"
      class="mb-5"
    >
      <v-card-title class="bg-primary text-white text-h6 pa-3">
        <v-icon class="me-2">
          mdi-plus
        </v-icon>
        Új csoport
      </v-card-title>
      <v-card-text class="pa-4">
        <v-row dense>
          <v-col
            cols="12"
            sm="4"
          >
            <v-text-field
              v-model="newGroup.name"
              label="Csoport neve"
              variant="outlined"
              density="comfortable"
              hide-details
            />
          </v-col>
          <v-col
            cols="6"
            sm="2"
          >
            <v-text-field
              v-model.number="newGroup.min_choices"
              label="Min."
              type="number"
              variant="outlined"
              density="comfortable"
              hide-details
              :min="0"
            />
          </v-col>
          <v-col
            cols="6"
            sm="2"
          >
            <v-text-field
              v-model.number="newGroup.max_choices"
              label="Max."
              type="number"
              variant="outlined"
              density="comfortable"
              hide-details
              :min="1"
            />
          </v-col>
          <v-col
            cols="12"
            sm="2"
            class="d-flex align-center"
          >
            <v-checkbox
              v-model="newGroup.required"
              label="Kötelező"
              hide-details
              density="comfortable"
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
              :disabled="!newGroup.name"
              @click="createGroup"
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

    <!-- Group list -->
    <v-progress-linear
      v-if="loading"
      indeterminate
      color="primary"
      class="mb-4"
    />

    <div
      v-if="groups.length === 0 && !loading"
      class="text-center py-10 text-medium-emphasis"
    >
      <v-icon
        size="48"
        class="mb-2"
      >
        mdi-tune-variant
      </v-icon>
      <p>Még nincsenek opció csoportok. Hozz létre egyet!</p>
    </div>

    <v-expansion-panels
      v-model="openPanels"
      multiple
      variant="accordion"
    >
      <v-expansion-panel
        v-for="group in groups"
        :key="group.id"
        class="mb-2"
      >
        <v-expansion-panel-title>
          <div class="d-flex align-center gap-2 flex-grow-1">
            <span class="font-weight-medium">{{ group.name }}</span>
            <v-chip
              v-if="group.min_choices > 0"
              size="x-small"
              color="primary"
              variant="tonal"
            >
              kötelező
            </v-chip>
            <v-chip
              size="x-small"
              color="primary"
              variant="outlined"
            >
              {{ group.min_choices }}–{{ group.max_choices }} választás
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
                @click.stop="startEditGroup(group)"
              />
              <v-btn
                icon="mdi-delete"
                size="small"
                variant="text"
                color="error"
                @click.stop="deleteGroup(group)"
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
            v-if="editingGroupId === group.id"
            class="pa-4 border-b"
          >
            <v-row dense>
              <v-col
                cols="12"
                sm="4"
              >
                <v-text-field
                  v-model="editGroupForm.name"
                  label="Név"
                  variant="outlined"
                  density="compact"
                  hide-details
                />
              </v-col>
              <v-col
                cols="5"
                sm="2"
              >
                <v-text-field
                  v-model.number="editGroupForm.min_choices"
                  label="Min."
                  type="number"
                  variant="outlined"
                  density="compact"
                  hide-details
                />
              </v-col>
              <v-col
                cols="5"
                sm="2"
              >
                <v-text-field
                  v-model.number="editGroupForm.max_choices"
                  label="Max."
                  type="number"
                  variant="outlined"
                  density="compact"
                  hide-details
                />
              </v-col>
              <v-col
                cols="12"
                sm="2"
                class="d-flex align-center"
              >
                <v-checkbox
                  v-model="editGroupForm.required"
                  label="Kötelező"
                  hide-details
                  density="compact"
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
                  @click="saveGroup(group.id)"
                >
                  Mentés
                </v-btn>
                <v-btn
                  size="small"
                  variant="text"
                  @click="editingGroupId = null"
                >
                  Mégse
                </v-btn>
              </v-col>
            </v-row>
          </div>

          <!-- Choices list -->
          <v-list
            density="compact"
            class="pa-0"
          >
            <v-list-item
              v-for="choice in group.choices"
              :key="choice.id"
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

              <template v-if="editingChoiceId === choice.id">
                <div class="d-flex align-start gap-2 flex-wrap pt-5 pb-1">
                  <v-text-field
                    v-model="editChoiceForm.name"
                    label="Név"
                    variant="outlined"
                    density="compact"
                    hide-details
                    style="min-width: 160px; max-width: 240px"
                  />
                  <v-text-field
                    v-model.number="editChoiceForm.price_delta"
                    label="Ár (Ft)"
                    type="text"
                    variant="outlined"
                    density="compact"
                    hide-details="auto"
                    :rules="[v => Number.isInteger(v) || 'Csak szám adható meg']"
                    style="max-width: 150px"
                  />
                  <v-btn
                    color="primary"
                    size="small"
                    variant="elevated"
                    class="mt-2"
                    @click="saveChoice(group.id, choice.id)"
                  >
                    Mentés
                  </v-btn>
                  <v-btn
                    size="small"
                    variant="text"
                    class="mt-2"
                    @click="editingChoiceId = null"
                  >
                    Mégse
                  </v-btn>
                </div>
              </template>

              <template v-else>
                <v-list-item-title class="text-body-2">
                  {{ choice.name }}
                  <span class="text-caption text-medium-emphasis ms-2">
                    {{ formatDelta(choice.price_delta) }}
                  </span>
                </v-list-item-title>
              </template>

              <template #append>
                <div
                  v-if="editingChoiceId !== choice.id"
                  class="d-flex"
                >
                  <v-btn
                    icon="mdi-pencil"
                    size="x-small"
                    variant="text"
                    color="primary"
                    @click="startEditChoice(choice)"
                  />
                  <v-btn
                    icon="mdi-delete"
                    size="x-small"
                    variant="text"
                    color="error"
                    @click="deleteChoice(group, choice)"
                  />
                </div>
              </template>
            </v-list-item>

            <!-- Add choice row -->
            <v-list-item class="px-3 pb-3">
              <div class="d-flex align-start gap-2 flex-wrap pt-5">
                <v-text-field
                  v-model="newChoices[group.id].name"
                  label="Új opció neve"
                  variant="outlined"
                  density="compact"
                  hide-details
                  style="min-width: 180px; max-width: 260px"
                />
                <v-text-field
                  v-model.number="newChoices[group.id].price_delta"
                  label="Ár (Ft)"
                  type="text"
                  variant="outlined"
                  density="compact"
                  hide-details="auto"
                  :rules="[v => Number.isInteger(v) || 'Csak szám adható meg']"
                  style="max-width: 160px"
                />
                <v-btn
                  color="primary"
                  size="small"
                  variant="elevated"
                  class="mt-2"
                  :disabled="!newChoices[group.id].name"
                  @click="addChoice(group.id)"
                >
                  <v-icon start>
                    mdi-plus
                  </v-icon>
                  Hozzáadás
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
import { useOptionGroupsStore } from '@/stores/option_groups'

export default {
  name: 'VendorOptionGroupManager',
  setup() {
    const optionGroupsStore = useOptionGroupsStore()
    return { optionGroupsStore }
  },
  data() {
    return {
      loading: false,
      saving: false,
      openPanels: [],
      editingGroupId: null,
      editingChoiceId: null,
      editGroupForm: { name: '', min_choices: 0, max_choices: 1, required: false, index: 0 },
      editChoiceForm: { name: '', price_delta: 0, index: 0 },
      newGroup: { name: '', min_choices: 0, max_choices: 1, required: false, index: 0 },
      newChoices: {},
      snackbar: { show: false, text: '', color: 'success' },
    }
  },
  computed: {
    vendorId() {
      return this.$route.params.id
    },
    groups() {
      return this.optionGroupsStore.forVendor(this.vendorId)
    },
  },
  watch: {
    groups(val) {
      for (const g of val) {
        if (!this.newChoices[g.id]) {
          this.newChoices[g.id] = { name: '', price_delta: 0, index: 0 }
        }
      }
    },
  },
  async mounted() {
    this.loading = true
    await this.optionGroupsStore.fetchByVendor(this.vendorId)
    this.loading = false
  },
  methods: {
    showSnackbar(text, color = 'success') {
      this.snackbar = { show: true, text, color }
    },

    formatDelta(delta) {
      if (delta === 0) return 'ingyenes'
      return (delta > 0 ? '+' : '') + delta + ' Ft'
    },

    async createGroup() {
      this.saving = true
      try {
        await this.optionGroupsStore.createGroup(this.vendorId, { ...this.newGroup, name: this.newGroup.name.trim() })
        this.newGroup = { name: '', min_choices: 0, max_choices: 1, required: false, index: 0 }
        this.showSnackbar('Csoport létrehozva')
      } catch {
        this.showSnackbar('Hiba történt', 'error')
      } finally {
        this.saving = false
      }
    },

    startEditGroup(group) {
      const idx = this.groups.findIndex(g => g.id === group.id)
      if (idx !== -1 && !this.openPanels.includes(idx)) {
        this.openPanels = [...this.openPanels, idx]
      }
      this.editingGroupId = group.id
      this.editGroupForm = {
        name: group.name,
        min_choices: group.min_choices,
        max_choices: group.max_choices,
        required: group.required,
        index: group.index,
      }
    },

    async saveGroup(groupId) {
      try {
        await this.optionGroupsStore.updateGroup(this.vendorId, groupId, { ...this.editGroupForm, name: this.editGroupForm.name.trim() })
        this.editingGroupId = null
        this.showSnackbar('Csoport mentve')
      } catch {
        this.showSnackbar('Hiba történt', 'error')
      }
    },

    async deleteGroup(group) {
      try {
        await this.optionGroupsStore.deleteGroup(this.vendorId, group.id)
        this.showSnackbar('Csoport törölve')
      } catch (e) {
        const msg = e?.response?.data?.error || 'Hiba történt'
        this.showSnackbar(msg, 'error')
      }
    },

    async addChoice(groupId) {
      const form = this.newChoices[groupId]
      try {
        await this.optionGroupsStore.addChoice(this.vendorId, groupId, {
          name: form.name.trim(),
          price_delta: form.price_delta || 0,
          index: (this.groups.find(g => g.id === groupId)?.choices?.length ?? 0),
        })
        this.newChoices[groupId] = { name: '', price_delta: 0, index: 0 }
        this.showSnackbar('Választás hozzáadva')
      } catch {
        this.showSnackbar('Hiba történt', 'error')
      }
    },

    startEditChoice(choice) {
      this.editingChoiceId = choice.id
      this.editChoiceForm = { name: choice.name, price_delta: choice.price_delta, index: choice.index }
    },

    async saveChoice(groupId, choiceId) {
      try {
        await this.optionGroupsStore.updateChoice(this.vendorId, groupId, choiceId, { ...this.editChoiceForm, name: this.editChoiceForm.name.trim() })
        this.editingChoiceId = null
        this.showSnackbar('Választás mentve')
      } catch {
        this.showSnackbar('Hiba történt', 'error')
      }
    },

    async deleteChoice(group, choice) {
      try {
        await this.optionGroupsStore.deleteChoice(this.vendorId, group.id, choice.id)
        this.showSnackbar('Választás törölve')
      } catch (e) {
        const msg = e?.response?.data?.error || 'Hiba történt'
        this.showSnackbar(msg, 'error')
      }
    },
  },
}
</script>

<style scoped>
.gap-2 { gap: 8px; }
</style>
