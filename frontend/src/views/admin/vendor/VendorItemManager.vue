<template>
  <v-container
    fluid
    class="pa-4"
    max-width="1400"
  >
    <v-row
      align="center"
      no-gutters
    >
      <v-col>
        <h2 class="text-h5 font-weight-bold">
          <v-icon class="me-2">
            mdi-food
          </v-icon>
          Menü kezelés
        </h2>
      </v-col>
    </v-row>
    <!-- Add New Item Form -->
    <ItemForm
      v-model="newItem"
      :loading="isLoading"
      @submit="addToMenu"
    />

    <v-divider class="my-4" />

    <!-- Search Section -->
    <SearchForm
      v-model="searchString"
      @search="search"
    />

    <v-divider class="my-4" />

    <!-- Items Data Table -->
    <ItemsDataTable
      :items="items"
      :loading="isLoading"
      :sortable="true"
      @edit-item="editItem"
      @update-item="updateItem"
      @cancel-edit="cancelEditItem"
      @duplicate-item="duplicateItem"
      @move-item="showMoveDialog"
      @copy-item="showCopyDialog"
      @delete-item="deleteItem"
      @reorder-items="reorderItems"
      @edit-size="editSize"
      @update-size="updateSize"
      @cancel-size-edit="cancelSizeEdit"
      @add-size="newSize"
      @duplicate-size="duplicateSize"
      @delete-size="deleteSize"
      @reorder-sizes="reorderSizes"
    />

    <!-- Pagination -->
    <v-pagination
      v-model="currentPage"
      :length="Math.ceil(totalCount / limit)"
      :total-visible="7"
      class="mt-4"
      @update:model-value="handlePageChange"
    />

    <!-- Move Item Dialog -->
    <MenuSelectionDialog
      v-model="showMovePopup"
      title="Étel áthelyezése"
      :getter-func="vendorStore.fetchMenus"
      @confirm="moveItem"
    />

    <!-- Copy Item Dialog -->
    <MenuSelectionDialog
      v-model="showCopyPopup"
      title="Étel másolása"
      :getter-func="vendorStore.fetchMenus"
      @confirm="copyItem"
    />

    <!-- Success/Error Snackbar -->
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
import { useAuth } from "@/stores/auth";
import { useMenuStore } from "@/stores/menu";
import { useItemStore } from "@/stores/item";
import { useSizeStore } from "@/stores/size";
import { useVendorStore } from "@/stores/vendor";
import ItemForm from "@/components/item-manager/ItemForm.vue";
import SearchForm from "@/components/item-manager/SearchForm.vue";
import ItemsDataTable from "@/components/item-manager/ItemsDataTable.vue";
import MenuSelectionDialog from "@/components/item-manager/MenuSelectionDialog.vue";

export default {
  name: "MenuItemManager",
  components: {
    ItemForm,
    SearchForm,
    ItemsDataTable,
    MenuSelectionDialog
  },
  setup() {
    const auth = useAuth();
    const menuStore = useMenuStore();
    const itemStore = useItemStore();
    const sizeStore = useSizeStore();
    const vendorStore = useVendorStore();
    return {
      auth,
      menuStore,
      itemStore,
      sizeStore,
      vendorStore
    }
  },
  data() {
    return {
      newItem: {
        name: "",
        description: "",
        category: "",
        index: 0,
      },
      items: [],
      searchString: "",
      isLoading: true,
      showCopyPopup: false,
      showMovePopup: false,
      selectedItem: null,
      selectedMenu: null,
      limit: null,
      currentPage: 1,
      totalCount: 0,
      snackbar: {
        show: false,
        text: '',
        color: 'success'
      }
    }
  },
  mounted() {
    this.getItemList()
  },
  methods: {
    showSnackbar(text, color = 'success') {
      this.snackbar = { show: true, text, color };
    },

    handlePageChange(page) {
      this.currentPage = page;
      this.getItemList()
    },

    async getItemList() {
      try {
        this.isLoading = true;
        const response = await this.menuStore.fetch(this.$route.params.menuId, {
          "search": this.searchString ? this.searchString : null,
          "limit": this.limit,
          "page": this.limit ? this.currentPage : null
        });

        if (response.status === 200) {
          const menuItemsArray = response.data.data.items.map(item => ({
            ...item,
            isEditing: false,
            sizes: item.sizes.map(size => ({
              ...size,
              isEditing: false
            }))
          }));

          this.currentPage = response.data.data.page;
          this.limit = response.data.data.limit;
          this.totalCount = response.data.data.total_count;
          this.items = menuItemsArray;
        }
      } catch (error) {
        this.showSnackbar('Hiba történt az adatok betöltése során', 'error');
      } finally {
        this.isLoading = false;
      }
    },

    async addToMenu() {
      try {
        this.newItem.menu_id = this.$route.params.menuId;
        const response = await this.itemStore.add(this.newItem);

        if (response.status === 201) {
          this.showSnackbar('Étel sikeresen hozzáadva');
          this.newItem = { name: "", description: "", category: "", index: 0 };
          this.getItemList();
        }
      } catch (error) {
        this.showSnackbar('Hiba történt az étel hozzáadása során', 'error');
      }
    },

    editItem(item) {
      const index = this.items.findIndex(i => i.id === item.id);
      if (index !== -1) {
        this.items[index] = { ...item, isEditing: true };
      }
    },

    cancelEditItem(item) {
      const index = this.items.findIndex(i => i.id === item.id);
      if (index !== -1) {
        this.items[index] = { ...item, isEditing: false };
      }
    },

    async updateItem(item) {
      try {
        const itemData = { ...item };
        delete itemData.isEditing;
        delete itemData.sizes;
        itemData.menu_id = this.$route.params.menuId;

        const response = await this.itemStore.update(item.id, itemData);

        if (response.status === 200) {
          this.showSnackbar('Étel sikeresen frissítve');
          this.getItemList();
        }
      } catch (error) {
        this.showSnackbar('Hiba történt a frissítés során', 'error');
      }
    },

    async duplicateItem(item) {
      try {
        const itemData = { ...item };
        delete itemData.id;
        delete itemData.isEditing;
        const sizes = [...itemData.sizes];
        delete itemData.sizes;
        itemData.name = `${itemData.name} (másolat)`;
        itemData.menu_id = this.$route.params.menuId;

        const response = await this.itemStore.add(itemData);

        if (response.status === 201) {
          const newItemId = response.data.data.id;

          // Copy sizes
          for (const size of sizes) {
            const sizeData = { ...size };
            delete sizeData.id;
            delete sizeData.isEditing;
            sizeData.menu_item_id = newItemId;
            await this.sizeStore.add(sizeData);
          }

          this.showSnackbar('Étel sikeresen duplikálva');
          this.getItemList();
        }
      } catch (error) {
        this.showSnackbar('Hiba történt a duplikálás során', 'error');
      }
    },

    showMoveDialog(item) {
      this.selectedItem = item;
      this.showMovePopup = true;
    },

    showCopyDialog(item) {
      this.selectedItem = item;
      this.showCopyPopup = true;
    },

    async moveItem(menu) {
      try {
        const item = { ...this.selectedItem };
        delete item.isEditing;
        delete item.sizes;
        item.menu_id = menu.id;

        const response = await this.itemStore.update(item.id, item);

        if (response.status === 200) {
          this.showSnackbar('Étel sikeresen áthelyezve');
          this.showMovePopup = false;
          this.getItemList();
        }
      } catch (error) {
        this.showSnackbar('Hiba történt az áthelyezés során', 'error');
      }
    },

    async copyItem(menu) {
      try {
        const item = { ...this.selectedItem };
        delete item.isEditing;
        const sizes = [...item.sizes];
        delete item.sizes;
        delete item.id;
        item.menu_id = menu.id;

        const response = await this.itemStore.add(item);

        if (response.status === 201) {
          const newItemId = response.data.data.id;

          for (const size of sizes) {
            const sizeData = { ...size };
            delete sizeData.isEditing;
            delete sizeData.id;
            sizeData.menu_item_id = newItemId;
            await this.sizeStore.add(sizeData);
          }

          this.showSnackbar('Étel sikeresen másolva');
          this.showCopyPopup = false;
          this.getItemList();
        }
      } catch (error) {
        this.showSnackbar('Hiba történt a másolás során', 'error');
      }
    },

    async deleteItem(item) {
      try {
        const response = await this.itemStore.delete(item.id);

        if (response.status === 200) {
          this.showSnackbar('Étel sikeresen törölve');
          this.getItemList();
        }
      } catch (error) {
        this.showSnackbar('Hiba történt a törlés során', 'error');
      }
    },

    async reorderItems(items) {
      try {
        const changedItems = [];

        items.forEach((item, index) => {
          const newIndex = index + 1; // 1-based indexing
          if (item.index !== newIndex) {
            changedItems.push({
              id: item.id,
              index: newIndex
            });
          }
        });

        if (changedItems.length === 0) {
          this.showSnackbar('Nincs változás a sorrendben');
          return;
        }

        // Call bulk update API
        await this.itemStore.bulkUpdateIndices(changedItems);

        this.showSnackbar(`${changedItems.length} elem sorrendje sikeresen frissítve`);
        this.getItemList();
      } catch (error) {
        console.error('Bulk update error:', error);
        this.showSnackbar('Hiba történt a sorrend frissítése során', 'error');
      }
    },

    search() {
      this.currentPage = 1;
      this.getItemList();
    },

    newSize(itemId) {
      const itemIndex = this.items.findIndex(item => item.id === itemId);
      if (itemIndex !== -1) {
        this.items[itemIndex].sizes.push({
          id: -1,
          name: "",
          price: 0,
          quantity: 0,
          unlimited: true,
          index: this.items[itemIndex].sizes.length,
          isEditing: true
        });
      }
    },

    editSize(itemId, size) {
      const itemIndex = this.items.findIndex(item => item.id === itemId);
      if (itemIndex !== -1) {
        const sizeIndex = this.items[itemIndex].sizes.findIndex(s => s.id === size.id);
        if (sizeIndex !== -1) {
          this.items[itemIndex].sizes[sizeIndex] = { ...size, isEditing: true };
        }
      }
    },

    cancelSizeEdit(itemId, size) {
      const itemIndex = this.items.findIndex(item => item.id === itemId);
      if (itemIndex !== -1) {
        const sizeIndex = this.items[itemIndex].sizes.findIndex(s => s.id === size.id);
        if (sizeIndex !== -1) {
          if (size.id === -1) {
            // Remove new size if cancelled
            this.items[itemIndex].sizes.splice(sizeIndex, 1);
          } else {
            this.items[itemIndex].sizes[sizeIndex] = { ...size, isEditing: false };
          }
        }
      }
    },

    async updateSize(itemId, size) {
      try {
        const sizeData = { ...size };
        delete sizeData.isEditing;
        sizeData.menu_item_id = itemId;

        if (size.id === -1) {
          delete sizeData.id;
          await this.sizeStore.add(sizeData);
        } else {
          await this.sizeStore.update(size.id, sizeData);
        }

        this.showSnackbar('Méret sikeresen frissítve');
        this.getItemList();
      } catch (error) {
        this.showSnackbar('Hiba történt a méret frissítése során', 'error');
      }
    },

    async duplicateSize(itemId, size) {
      try {
        const sizeData = { ...size };
        delete sizeData.id;
        delete sizeData.isEditing;
        sizeData.name = `${sizeData.name} (másolat)`;
        sizeData.menu_item_id = itemId;

        await this.sizeStore.add(sizeData);
        this.showSnackbar('Méret sikeresen duplikálva');
        this.getItemList();
      } catch (error) {
        this.showSnackbar('Hiba történt a duplikálás során', 'error');
      }
    },

    async deleteSize(itemId, size) {
      try {
        await this.sizeStore.delete(size.id);
        this.showSnackbar('Méret sikeresen törölve');
        this.getItemList();
      } catch (error) {
        this.showSnackbar('Hiba történt a törlés során', 'error');
      }
    },

    async reorderSizes(itemId, sizes) {
      try {
        for (let i = 0; i < sizes.length; i++) {
          if (sizes[i].index !== i) {
            sizes[i].index = i;
            const sizeData = { ...sizes[i] };
            delete sizeData.isEditing;
            sizeData.menu_item_id = itemId;
            await this.sizeStore.update(sizes[i].id, sizeData);
          }
        }
        this.showSnackbar('Méretek sorrendje sikeresen frissítve');
        this.getItemList();
      } catch (error) {
        this.showSnackbar('Hiba történt a sorrend frissítése során', 'error');
      }
    }
  }
};
</script>
