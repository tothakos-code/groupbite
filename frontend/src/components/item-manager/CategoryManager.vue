<template>
  <v-container
    fluid
    class="pa-4"
  >
    <!-- Add new category -->
    <v-card
      elevation="2"
      class="mb-4"
    >
      <v-card-title class="text-h6 bg-primary text-white">
        <v-icon class="me-2">
          mdi-tag-plus
        </v-icon>
        Új kategória
      </v-card-title>
      <v-card-text class="pa-4">
        <v-row align="center">
          <v-col>
            <v-text-field
              v-model="newName"
              label="Kategória neve"
              variant="outlined"
              density="comfortable"
              hide-details
              @keyup.enter="create"
            />
          </v-col>
          <v-col cols="auto">
            <v-btn
              color="primary"
              variant="elevated"
              size="large"
              :loading="creating"
              :disabled="!newName.trim()"
              @click="create"
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

    <!-- Categories list -->
    <v-card elevation="2">
      <v-card-title class="text-h6 bg-primary text-white">
        <v-icon class="me-2">
          mdi-tag-multiple
        </v-icon>
        Kategóriák
      </v-card-title>

      <v-list
        v-if="categories.length"
        lines="one"
      >
        <template
          v-for="(cat, idx) in categories"
          :key="cat.id"
        >
          <v-divider v-if="idx > 0" />
          <v-list-item :ripple="false">
            <template v-if="editingId !== cat.id">
              <v-list-item-title class="text-body-1">
                {{ cat.name }}
              </v-list-item-title>
            </template>
            <template v-else>
              <v-text-field
                v-model="editName"
                density="compact"
                variant="outlined"
                hide-details
                autofocus
                style="max-width: 320px"
                @keyup.enter="save(cat)"
                @keyup.esc="cancelEdit"
              />
            </template>

            <template #append>
              <template v-if="editingId !== cat.id">
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  class="me-1"
                  @click="startEdit(cat)"
                >
                  <v-icon>mdi-pencil</v-icon>
                </v-btn>
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  color="error"
                  @click="confirmDelete(cat)"
                >
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </template>
              <template v-else>
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  color="success"
                  :loading="saving"
                  class="me-1"
                  @click="save(cat)"
                >
                  <v-icon>mdi-check</v-icon>
                </v-btn>
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  @click="cancelEdit"
                >
                  <v-icon>mdi-close</v-icon>
                </v-btn>
              </template>
            </template>
          </v-list-item>
        </template>
      </v-list>

      <div
        v-else
        class="pa-8 text-center text-medium-emphasis"
      >
        Nincsenek kategóriák
      </div>
    </v-card>

    <!-- Delete confirmation dialog -->
    <v-dialog
      v-model="deleteDialog"
      max-width="400"
    >
      <v-card>
        <v-card-title class="text-h6">
          Kategória törlése
        </v-card-title>
        <v-card-text>
          Biztosan törölni szeretnéd a <strong>{{ categoryToDelete?.name }}</strong> kategóriát?
          <div class="text-caption text-medium-emphasis mt-2">
            Csak üres (elemek nélküli) kategóriák törölhetők.
          </div>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn
            variant="outlined"
            @click="deleteDialog = false"
          >
            Mégse
          </v-btn>
          <v-btn
            color="error"
            variant="flat"
            :loading="deleting"
            @click="deleteCategory"
          >
            Törlés
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Snackbar -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="3000"
    >
      {{ snackbar.text }}
      <template #actions>
        <v-btn
          color="white"
          variant="text"
          @click="snackbar.show = false"
        >
          Bezárás
        </v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script>
import { useCategoriesStore } from "@/stores/categories";

export default {
  name: "CategoryManager",
  props: {
    vendorId: {
      type: String,
      required: true,
    },
  },
  setup() {
    const categoriesStore = useCategoriesStore();
    return { categoriesStore };
  },
  data() {
    return {
      newName: "",
      creating: false,
      editingId: null,
      editName: "",
      saving: false,
      deleteDialog: false,
      categoryToDelete: null,
      deleting: false,
      snackbar: { show: false, text: "", color: "success" },
    };
  },
  computed: {
    categories() {
      return this.categoriesStore.byVendor[this.vendorId] || [];
    },
  },
  mounted() {
    this.categoriesStore.fetchByVendor(this.vendorId);
  },
  methods: {
    showSnackbar(text, color = "success") {
      this.snackbar = { show: true, text, color };
    },

    async create() {
      if (!this.newName.trim()) return;
      try {
        this.creating = true;
        await this.categoriesStore.createCategory(this.vendorId, this.newName.trim());
        this.showSnackbar("Kategória sikeresen létrehozva");
        this.newName = "";
      } catch {
        this.showSnackbar("Hiba történt a létrehozás során", "error");
      } finally {
        this.creating = false;
      }
    },

    startEdit(cat) {
      this.editingId = cat.id;
      this.editName = cat.name;
    },

    cancelEdit() {
      this.editingId = null;
      this.editName = "";
    },

    async save(cat) {
      if (!this.editName.trim() || this.editName.trim() === cat.name) {
        this.cancelEdit();
        return;
      }
      try {
        this.saving = true;
        await this.categoriesStore.renameCategory(this.vendorId, cat.id, this.editName.trim());
        this.showSnackbar("Kategória sikeresen átnevezve");
      } catch {
        this.showSnackbar("Hiba történt az átnevezés során", "error");
      } finally {
        this.saving = false;
        this.cancelEdit();
      }
    },

    confirmDelete(cat) {
      this.categoryToDelete = cat;
      this.deleteDialog = true;
    },

    async deleteCategory() {
      try {
        this.deleting = true;
        await this.categoriesStore.deleteCategory(this.vendorId, this.categoryToDelete.id);
        this.showSnackbar("Kategória sikeresen törölve");
        this.deleteDialog = false;
      } catch (err) {
        const msg = err?.response?.data?.error || "Hiba történt a törlés során";
        this.showSnackbar(msg, "error");
        this.deleteDialog = false;
      } finally {
        this.deleting = false;
        this.categoryToDelete = null;
      }
    },
  },
};
</script>
