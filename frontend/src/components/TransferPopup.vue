<template>
  <v-tooltip location="bottom">
    <template #activator="{ props }">
      <v-btn
        id="transferBasketButton"
        v-bind="props"
        variant="elevated"
        color="primary"
        class="me-2"
        @click="openPopup()"
      >
        Rendelés
        <v-icon class="ml-2">
          mdi-truck
        </v-icon>
      </v-btn>
    </template>
    <span>Rendelése leadás megkezdése</span>
  </v-tooltip>

  <v-dialog
    v-model="optionDialogVisible"
    max-width="600"
    :persistent="false"
    scrim
  >
    <v-card>
      <v-card-title class="text-h5 text-center">
        Rendelés mód kiválasztása
      </v-card-title>

      <v-card-text>
        <v-row
          dense
          align="stretch"
        >
          <!-- Full Auto -->
          <v-col
            cols="12"
            sm="4"
          >
            <v-card
              class="d-flex flex-column align-center justify-center py-6 px-3 text-center cursor-pointer hover:shadow-md transition"
              color="success"
              variant="elevated"
              :disabled="!enable_full_automatic_order"
              @click="startFullAutoOrder"
            >
              <v-icon size="48">
                mdi-robot
              </v-icon>
              <div class="mt-3 font-weight-medium text-subtitle-1">
                Automatikus
              </div>
              <div class="text-body-2 mt-1">
                Rendelés áttöltése és/vagy rendelése az eredeti oldalon keresztül.
              </div>
            </v-card>
          </v-col>

          <!-- Semi Auto -->
          <v-col
            cols="12"
            sm="4"
          >
            <v-card
              class="fill-height d-flex flex-column align-center justify-center py-6 px-3 text-center cursor-pointer hover:shadow-md transition"
              color="info"
              variant="elevated"
              :loading="emailSending"
              :disabled="!enable_email_order"
              @click="confirmSemiAuto = true"
            >
              <v-icon size="48">
                mdi-email-fast-outline
              </v-icon>
              <div class="mt-3 font-weight-medium text-subtitle-1">
                Félig automatikus
              </div>
              <div class="text-body-2 mt-1">
                Lezárja és továbbítja a rendelést emailben.
              </div>
            </v-card>
          </v-col>

          <!-- Manual -->
          <v-col
            cols="12"
            sm="4"
          >
            <v-card
              class="fill-height d-flex flex-column align-center justify-center py-6 px-3 text-center cursor-pointer hover:shadow-md transition"
              color="primary"
              variant="elevated"
              :disabled="!enable_manual_order"
              @click="startManualOrder"
            >
              <v-icon size="48">
                mdi-hand-pointing-up
              </v-icon>
              <div class="mt-3 font-weight-medium text-subtitle-1">
                Manuális
              </div>
              <div class="text-body-2 mt-1">
                Minden lépést te végzel el kézzel, maximális kontroll.
              </div>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-dialog>

  <v-dialog
    v-model="confirmSemiAuto"
    max-width="500"
    persistent
  >
    <v-card>
      <v-card-title class="text-h6">
        Biztosan folytatod?
      </v-card-title>

      <v-card-text>
        <v-alert
          type="info"
          variant="tonal"
          class="mb-2"
        >
          Ez a művelet lezárja a rendelést és elküldi emailben az érintett félnek. További módosítás nem lesz lehetséges.
        </v-alert>
        <p class="text-body-2">
          Ha megerősíted, a rendelés lezárul és a rendszer emailt küld automatikusan.
        </p>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn
          variant="text"
          @click="confirmSemiAuto = false"
        >
          Mégse
        </v-btn>
        <v-btn
          color="info"
          variant="elevated"
          :loading="emailSending"
          @click="confirmAndSendEmail"
        >
          Rendelés lezárása és email küldése
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>


  <!-- Main Order Dialog -->
  <v-dialog
    v-model="showInitial"
    max-width="800px"
    persistent
  >
    <v-card>
      <v-card-title class="text-h5">
        Rendelés áttöltése
      </v-card-title>

      <v-card-text>
        <v-row>
          <!-- Email Sending Section -->
          <v-card
            variant="outlined"
            class="mb-4"
          >
            <v-card-title class="text-subtitle-1">
              Email küldés
            </v-card-title>
            <v-card-text>
              <p class="text-body-2 mb-3">
                Nincs meg a minimum automatikus rendeléshez? Küld el az emailt itt!
              </p>
              <v-btn
                variant="elevated"
                color="info"
                :loading="emailSending"
                prepend-icon="mdi-email-send"
                @click="sendOrderEmail()"
              >
                Email küldés
              </v-btn>
            </v-card-text>
          </v-card>
        </v-row>
        <v-row>
          <v-alert
            type="info"
            variant="tonal"
            class="mb-4"
          >
            A lista automatikusan frissül, ha valaki változtat a kosarán. Pipáld ki ha átraktad VAGY másold a teljes rendelést szövegként
          </v-alert>
        </v-row>

        <v-row>
          <v-col>
            <v-card-subtitle class="d-flex justify-space-between align-center pa-3">
              <div>
                <span class="text-body-2">
                  {{ tickedItemsCount }} / {{ activeItemsCount }} elem kijelölve
                </span>
              </div>

              <div class="ms-2 d-flex gap-2">
                <v-btn
                  size="small"
                  variant="elevated"
                  color="primary"
                  :disabled="allActiveItemsTicked || activeItemsCount === 0"
                  @click="tickAllItems"
                >
                  Mind kijelöl
                </v-btn>

                <v-btn
                  size="small"
                  variant="elevated"
                  color="primary"
                  :disabled="!someActiveItemsTicked"
                  @click="untickAllItems"
                >
                  Mind törli
                </v-btn>
                <v-btn
                  size="small"
                  variant="elevated"
                  color="primary"
                  @click="doCopyOrder()"
                >
                  Szövegesen másol
                  <v-icon class="ml-2">
                    mdi-content-copy
                  </v-icon>
                </v-btn>
              </div>
            </v-card-subtitle>

            <v-divider />

            <!-- Items List -->
            <v-list density="compact">
              <!-- Individual items -->
              <v-list-item
                v-for="item in orderItems"
                :key="item.item_id"

                :class="{
                  'bg-grey-lighten-4': item.deleted,
                  'bg-green-lighten-5': item.tick && !item.deleted
                }"
              >
                <template #prepend>
                  <v-checkbox
                    v-model="item.tick"
                    :disabled="item.deleted"
                    color="primary"
                    hide-details
                  />
                </template>

                <v-list-item-title
                  :class="{
                    'text-decoration-line-through text-grey': item.deleted,
                    'font-weight-bold': !item.tick && !item.deleted,
                    'text-success': item.tick && !item.deleted
                  }"
                >
                  <span class="text-h6 me-2">{{ item.quantity }}×</span>
                  {{ item.item_name }}
                  <span
                    v-if="item.size_name"
                    class="text-body-2 text-grey-darken-1"
                  >
                    ({{ item.size_name }})
                  </span>
                </v-list-item-title>


                <template #append>
                  <div class="d-flex align-center gap-2">
                    <!-- Status indicators -->
                    <v-icon
                      v-if="item.tick && !item.deleted"
                      color="success"
                      size="small"
                    >
                      mdi-check-circle
                    </v-icon>

                    <v-chip
                      v-if="item.deleted"
                      color="error"
                      variant="flat"
                      size="small"
                    >
                      Törölték
                    </v-chip>
                  </div>
                </template>
              </v-list-item>

              <!-- Empty state -->
              <v-list-item v-if="orderItems.length === 0">
                <v-list-item-title class="text-center text-grey">
                  Nincs termék a kosárban
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-col>
        </v-row>

        <v-card-actions
          v-if="orderItems.length > 0"
          class="justify-center"
        >
          <v-chip
            :color="tickedItemsCount === activeItemsCount && activeItemsCount > 0 ? 'success' : 'primary'"
            variant="flat"
          >
            {{ tickedItemsCount }} / {{ activeItemsCount }} elem feldolgozva
          </v-chip>
        </v-card-actions>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn
          variant="text"
          @click="showInitial = false"
        >
          Mégse
        </v-btn>
        <v-btn
          variant="elevated"
          color="primary"
          @click="closeOrder()"
        >
          Folytat
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Loading Overlay -->
  <v-overlay
    v-model="showSpinner"
    class="d-flex align-center justify-center"
  >
    <v-progress-circular
      indeterminate
      size="64"
      color="primary"
    />
  </v-overlay>

  <!-- Finish Order Dialog -->
  <v-dialog
    v-model="showFinish"
    max-width="600px"
    persistent
  >
    <v-card>
      <v-card-title class="text-h5">
        Rendelés befejezése
      </v-card-title>

      <v-card-text>
        <v-alert
          type="success"
          variant="tonal"
          class="mb-4"
        >
          Rendelés lezárva, további kosármódosítás letiltva.
        </v-alert>

        <v-card
          variant="outlined"
          class="mb-4"
        >
          <v-card-title class="text-subtitle-1">
            Rendelés megjegyzés példa:
          </v-card-title>
          <v-card-text>
            <div class="d-flex align-center">
              <v-sheet
                color="grey-lighten-4"
                class="pa-2 flex-grow-1 font-family-monospace"
                rounded
              >
                {{ orderDesc }}
              </v-sheet>
              <v-btn
                variant="text"
                icon="mdi-content-copy"
                class="ml-2"
                @click="doCopy()"
              />
            </div>
          </v-card-text>
        </v-card>

        <v-card
          variant="outlined"
          class="mb-4"
        >
          <v-card-title class="text-subtitle-1">
            Szállítási díj módosítása
          </v-card-title>
          <v-card-text>
            <p class="text-body-2 mb-2">
              Ha a szállítási díj eltérhet az alapértelmezetten megadottól (pl.: eltér a tényleges szállítás díj, rendszerhasználati díj felszámításra került) itt megtudod változtatni.
            </p>
            <p class="text-body-2 mb-2">
              A különböző extra díjak összegét írd be valuta nélkül
            </p>
            <p class="text-body-2 mb-3">
              Az alapértelmezett beállított díj: {{ vendorStore.selectedVendor.settings.transport_price.value }}
            </p>

            <v-text-field
              v-model.number="transport_price"
              type="number"
              label="A jelenlegi díj"
              variant="outlined"
              density="compact"
              :placeholder="transport_price.toString()"
            />
          </v-card-text>
        </v-card>

        <v-alert
          type="success"
          variant="tonal"
        >
          Köszönjük az ebédet!
        </v-alert>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn
          variant="elevated"
          color="primary"
          @click="changeTransportPrice()"
        >
          Befejez
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { useAuth } from "@/stores/auth";
import { useOrderStore } from "@/stores/order";
import { useVendorStore } from "@/stores/vendor";
import { copyText } from "vue3-clipboard";
import { notify } from "@kyvg/vue3-notification";
import { unref } from "vue";

export default {
  name: "TransferPopup",
  props: {
    enable_email_order: {
      type: Boolean,
      default: false
    },
    enable_manual_order: {
      type: Boolean,
      default: false
    },
    enable_full_automatic_order: {
      type: Boolean,
      default: false
    },
  },
  setup() {
    const auth = useAuth();
    const orderStore = useOrderStore();
    const vendorStore = useVendorStore();

    return {
      auth,
      orderStore,
      vendorStore
    }
  },
  data() {
    return {
      showInitial: false,
      showSpinner: false,
      showFinish: false,
      emailSending: false,
      optionDialogVisible: false,
      bulkActionInProgress: false,
      confirmSemiAuto: false,
      orderItems: [],
      psid: "",
      transport_price: unref(useVendorStore().selectedVendor.settings.transport_price.value)
    }
  },
  computed: {
    orderDesc() {
      return this.vendorStore.selectedVendor.settings.comment_example.value
    },
    tickedItemsCount() {
      return this.orderItems.filter(item => item.tick && !item.deleted).length;
    },

    activeItemsCount() {
      return this.orderItems.filter(item => !item.deleted).length;
    },

    allActiveItemsTicked() {
      const activeItems = this.orderItems.filter(item => !item.deleted);
      return activeItems.length > 0 && activeItems.every(item => item.tick);
    },

    someActiveItemsTicked() {
      return this.orderItems.some(item => item.tick && !item.deleted);
    }
  },
  watch: {
    'orderStore.basket': {
      handler(newBasket) {
        // Skip processing during bulk actions to prevent conflicts
        if (this.bulkActionInProgress) return;

        // Create new merged item map
        const newItemMap = this.createMergedBasketItems(newBasket);

        // Create map of current items for comparison
        const oldItemsMap = new Map(
          this.orderItems.map(item => [item.item_id, { ...item }])
        );

        // Process changes and get notifications
        const notifications = this.processItemChanges(newItemMap, oldItemsMap);

        // Update order items with sorting
        this.orderItems = Array.from(newItemMap.values())
          .sort((a, b) => {
            // Sort by category first, then by name
            const categoryCompare = a.category.localeCompare(b.category);
            if (categoryCompare !== 0) return categoryCompare;
            return a.item_name.localeCompare(b.item_name);
          });

        // Show notifications
        this.showNotifications(notifications);
      },
      deep: true,
      immediate: true
    }
  },
  methods: {
    openPopup() {
      if (this.orderStore.order.state_id === "closed") {
        notify({
          type: "warn",
          text: "A rendelést ma már elküldték",
        });
        return;
      } else {
        this.optionDialogVisible = true; // NEW: show option dialog first
      }
    },
    toggleAllItems(tickState) {
      this.bulkActionInProgress = true;

      this.orderItems.forEach(item => {
        if (!item.deleted) {
          item.tick = tickState;
        }
      });

      this.bulkActionInProgress = false;
    },

    tickAllItems() {
      this.toggleAllItems(true);
    },
    untickAllItems() {
      this.toggleAllItems(false);
    },
    createMergedBasketItems(basket) {
      const itemMap = new Map();

      // Flatten all basket items and merge by item_id
      Object.values(basket).forEach(userBasket => {
        userBasket.items.forEach(item => {
          const itemId = item.item_id;
          const quantity = Number(item.quantity);

          if (itemMap.has(itemId)) {
            itemMap.get(itemId).quantity += quantity;
          } else {
            itemMap.set(itemId, {
              ...item,
              quantity,
              tick: false,
              deleted: false
            });
          }
        });
      });

      return itemMap;
    },
    startFullAutoOrder() {
      this.optionDialogVisible = false;
      this.showFinish = true;
      // TODO: Trigger full auto API logic here if needed
    },
    startManualOrder() {
      this.optionDialogVisible = false;
      this.showInitial = true;
    },
    async confirmAndSendEmail() {
      this.confirmSemiAuto = false;
      this.optionDialogVisible = false;
      await this.sendOrderEmail().then(() => {
        this.showFinish = true;
      });
    },
    processItemChanges(newItemMap, oldItemsMap) {
       const notifications = [];

       // Process existing and new items
       for (const [itemId, newItem] of newItemMap) {
         const oldItem = oldItemsMap.get(itemId);

         if (oldItem) {
           // Item exists - check for quantity changes
           if (oldItem.quantity !== newItem.quantity) {
             newItem.tick = false;
             if (this.showInitial) {
               notifications.push({
                 type: "warn",
                 text: `${newItem.item_name} mennyisége megváltozott. A lista frissült!`
               });
             }
           } else {
             // Quantity unchanged - preserve tick state
             newItem.tick = oldItem.tick;
           }

           // Remove from old items map (remaining items will be considered deleted)
           oldItemsMap.delete(itemId);
         } else {
           // New item added
           if (this.showInitial) {
             notifications.push({
               type: "warn",
               text: `Új termék került a kosárba: ${newItem.item_name}. A lista frissült!`
             });
           }
         }
       }

       // Handle deleted items
       for (const [itemId, oldItem] of oldItemsMap) {
         if (oldItem.tick && !oldItem.deleted) {
           // Previously ticked item was deleted
           newItemMap.set(itemId, {
             ...oldItem,
             tick: false,
             deleted: true
           });

           if (this.showInitial) {
             notifications.push({
               type: "warn",
               text: `Egy terméket töröltek a kosárból amit már átraktál: ${oldItem.item_name}. A lista frissült!`
             });
           }
         } else if (oldItem.deleted) {
           // Keep deleted items in list
           newItemMap.set(itemId, {
             ...oldItem,
             tick: false,
             deleted: true
           });
         }
       }

       return notifications;
     },

     // Show notifications
     showNotifications(notifications) {
       notifications.forEach(notification => {
         notify(notification);
       });
   },
    closeOrder() {
      if (this.orderItems.length === 0) {
        notify({
          type: "warn",
          text: "Nincs mit megrendelni.",
        });
        return
      }
      if (!this.allActiveItemsTicked) {
        notify({
          type: "warn",
          text: "Minden sort kikell pipálnod mielött lezárhatod a rendelést.",
        });
        return
      }
      this.orderStore.close()

      this.showInitial = false;
      this.showFinish = true;
    },
    doCopyOrder() {
      let orderText = ""
      for (const item of this.orderItems) {
        if (item.deleted) {
          continue
        }
        orderText += this.vendorStore.selectedVendor.settings.order_text_template.value
          .replace("${quantity}", item.quantity)
          .replace("${item_name}", item.item_name)
          .replace("${size_name}", item.size_name)
          .replace("\\n", "\n");

        item.tick = true;
      }
      copyText(orderText, undefined, (error, event) => {
        if (error) {
          notify({
            type: "warn",
            text: "Nem sikerült a vágólapra másolás",
          });
          console.log(error)
        } else {
          notify({
            type: "info",
            text: "Rendelés vágólapra másolva",
          });
          console.log(event)
        }
      });
    },
    doCopy() {
      copyText(this.orderDesc, undefined, (error, event) => {
        if (error) {
          notify({
            type: "warn",
            text: "Nem sikerült a vágólapra másolás",
          });
          console.log(error)
        } else {
          notify({
            type: "info",
            text: "Rendelés vágólapra másolva",
          });
          console.log(event)
        }
      });
    },
    changeTransportPrice() {
      if (this.transport_price !== this.orderStore.transportFee) {
        this.orderStore.changeTransportPrice(this.transport_price)
      }
      this.showFinish = false;
    },
    async sendOrderEmail() {
      this.emailSending = true;
      try {
        await this.orderStore.sendOrderEmail()

        notify({
          type: "success",
          text: "Email sikeresen elküldve!",
        });

      } catch (error) {
        notify({
          type: "error",
          text: "Hiba történt az email küldése során.",
        });
        console.error('Email sending error:', error);
      } finally {
        this.emailSending = false;
      }
    }
  }
}
</script>

<style scoped>
.font-family-monospace {
  font-family: 'Courier New', monospace;
}
</style>
