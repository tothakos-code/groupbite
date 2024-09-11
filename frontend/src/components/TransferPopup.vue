<template>
  <button
    id="transferBasketButton"
    class="btn my-1"
    :class="['btn-outline-' + auth.getUserColor ]"
    @click="openPopup()"
  >
    Rendelés
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      fill="currentColor"
      class="bi bi-truck"
      viewBox="0 0 16 16"
    >
      <path d="M0 3.5A1.5 1.5 0 0 1 1.5 2h9A1.5 1.5 0 0 1 12 3.5V5h1.02a1.5 1.5 0 0 1 1.17.563l1.481 1.85a1.5 1.5 0 0 1 .329.938V10.5a1.5 1.5 0 0 1-1.5 1.5H14a2 2 0 1 1-4 0H5a2 2 0 1 1-3.998-.085A1.5 1.5 0 0 1 0 10.5v-7zm1.294 7.456A1.999 1.999 0 0 1 4.732 11h5.536a2.01 2.01 0 0 1 .732-.732V3.5a.5.5 0 0 0-.5-.5h-9a.5.5 0 0 0-.5.5v7a.5.5 0 0 0 .294.456zM12 10a2 2 0 0 1 1.732 1h.768a.5.5 0 0 0 .5-.5V8.35a.5.5 0 0 0-.11-.312l-1.48-1.85A.5.5 0 0 0 13.02 6H12v4zm-9 1a1 1 0 1 0 0 2 1 1 0 0 0 0-2zm9 0a1 1 0 1 0 0 2 1 1 0 0 0 0-2z" />
    </svg>
  </button>

  <Popup
    :show-modal="showInitial"
    title="Rendelés áttöltése"
    :large="true"
    @cancel="showInitial = false"
    @confirm="closeOrder()"
  >
    <div class="row">
      <div class="col-9 me-0 pe-0">
        <p>A lista automatikusan frissül, ha valaki változtat a kosarán. Pipáld ki ha átraktad VAGY másold a teljes rendelést szövegként</p>
      </div>
      <div class="col-3 text-end">
        <button
          type="button"
          name="button"
          title="Copy to clipboard"
          class="btn btn-sm ms-0"
          :class="['btn-outline-' + auth.getUserColor ]"
          @click="doCopyOrder()"
        >
          Másol
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="28"
            height="28"
            fill="currentColor"
            class="bi bi-clipboard2"
            viewBox="0 0 16 16"
          >
            <path d="M3.5 2a.5.5 0 0 0-.5.5v12a.5.5 0 0 0 .5.5h9a.5.5 0 0 0 .5-.5v-12a.5.5 0 0 0-.5-.5H12a.5.5 0 0 1 0-1h.5A1.5 1.5 0 0 1 14 2.5v12a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 2 14.5v-12A1.5 1.5 0 0 1 3.5 1H4a.5.5 0 0 1 0 1h-.5Z" />
            <path d="M10 .5a.5.5 0 0 0-.5-.5h-3a.5.5 0 0 0-.5.5.5.5 0 0 1-.5.5.5.5 0 0 0-.5.5V2a.5.5 0 0 0 .5.5h5A.5.5 0 0 0 11 2v-.5a.5.5 0 0 0-.5-.5.5.5 0 0 1-.5-.5Z" />
          </svg>
        </button>
      </div>
    </div>

    <div
      v-for="item in orderItems"
      :key="item.id"
      class="list-group-item d-flex justify-content-between align-items-center fs-4 rounded"
    >
      <span
        :class="{'text-decoration-line-through': item.deleted, 'fw-bold': !item.tick}"
        class="ms-1"
      >
        {{ item.quantity }}x {{ item.item_name }} {{ item.size_name }}
      </span>
      <span
        v-if="item.deleted"
        class="text-danger"
      >Törölték</span>
      <input
        v-model="item.tick"
        type="checkbox"
        class="form-check-input m-0 me-1"
        name=""
        :value="item.tick"
      >
    </div>
  </Popup>
  <teleport to="body">
    <div
      v-if="showSpinner"
      class="overlay d-flex justify-content-center"
    >
      <div
        class="spinner-border text-center text-dark"
        style="width: 4rem; height: 4rem; z-index: 20;"
        role="status"
      >
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
  </teleport>
  <Popup
    :show-modal="showFinish"
    title="Rendelés befejezése"
    @cancel="showFinish = false"
    @confirm="showFinish = false;"
  >
    <p>Rendelés lezárva, további kosármódosítás letiltva.</p>
    <p>
      Rendelés megjegyzés példa:
    </p>
    <div class="d-flex">
      <div class="border bg-light-subtle rounded ps-2">
        <code class="user-select-all">{{ orderDesc }}</code>
      </div>
      <button
        type="button"
        name="button"
        title="Copy to clipboard"
        class="btn "
        @click="doCopy()"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="28"
          height="28"
          fill="currentColor"
          class="bi bi-clipboard2"
          viewBox="0 0 16 16"
        >
          <path d="M3.5 2a.5.5 0 0 0-.5.5v12a.5.5 0 0 0 .5.5h9a.5.5 0 0 0 .5-.5v-12a.5.5 0 0 0-.5-.5H12a.5.5 0 0 1 0-1h.5A1.5 1.5 0 0 1 14 2.5v12a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 2 14.5v-12A1.5 1.5 0 0 1 3.5 1H4a.5.5 0 0 1 0 1h-.5Z" />
          <path d="M10 .5a.5.5 0 0 0-.5-.5h-3a.5.5 0 0 0-.5.5.5.5 0 0 1-.5.5.5.5 0 0 0-.5.5V2a.5.5 0 0 0 .5.5h5A.5.5 0 0 0 11 2v-.5a.5.5 0 0 0-.5-.5.5.5 0 0 1-.5-.5Z" />
        </svg>
      </button>
    </div>
    <br>
    <p>Köszönjük az ebédet!</p>
  </Popup>
</template>

<script>
import Popup from "./Popup.vue";
import { state, socket } from "@/main";
import { useAuth } from "@/stores/auth";
import { useBasket } from "@/stores/basket";
import { copyText } from "vue3-clipboard";
import { notify } from "@kyvg/vue3-notification";
import { watch } from "vue";

export default {
  name: "TransferPopup",
  components: {
    Popup
  },
  setup() {
    const auth = useAuth();
    const basket = useBasket();

    return {
      auth,
      basket
    }
  },
  data() {
    return {
      showInitial: false,
      showSpinner: false,
      showFinish: false,
      orderItems: [],
      psid: ""
    }
  },
  computed: {
    orderDesc() {
      return state.selected_vendor.settings.comment_example.value
    },
  },
  mounted() {

        watch(
          () => this.basket.basket,
          (newBasket) =>{
            let resultList = []
            for (const value of Object.values(newBasket)) {
              for (const item of value.items) {
                let i = item;
                i.quantity = item.quantity;
                i.tick = false;
                i.deleted = false;
                resultList.push(i);
              }
            }

            const itemMap = new Map();

            for (const item of resultList) {
                if (itemMap.has(item.item_id)) {
                    itemMap.get(item.item_id).quantity += Number(item.quantity);
                } else {
                    itemMap.set(item.item_id, { ...item, count: Number(item.quantity) });
                }
            }

            const oldMap = new Map(this.orderItems.map(item => [item.item_id, item]));

            for (const newItem of Array.from(itemMap.values())) {
                const oldItem = oldMap.get(newItem.item_id);
                if (oldItem) {
                    if (oldItem.quantity !== newItem.quantity) {
                        itemMap.set(newItem.item_id, {...newItem, tick: false})
                        if (this.showInitial) {
                          notify({
                            type: "warn",
                            text: newItem.item_name +" mennyisége megváltozott. A lista frissült!",
                          });
                        }
                    } else {
                      itemMap.set(newItem.item_id, {...newItem, tick: oldItem.tick})

                    }
                    oldMap.delete(newItem.item_id)
                } else {
                  if (this.showInitial) {
                    notify({
                      type: "warn",
                      text: "Új termék került a kosárba: " + newItem.item_name+". A lista frissült!",
                    });
                  }
                }
            }

            if (oldMap.size !== 0) {
              for (const oldItem of oldMap.values()) {
                if (oldItem.tick && !oldItem.deleted) {
                  itemMap.set(oldItem.item_id, {...oldItem, tick: false, deleted:true})
                  if (this.showInitial) {
                    notify({
                      type: "warn",
                      text: "Egy terméket töröltek a kosárból amit már átraktál: " + oldItem.item_name+". A lista frissült!",
                    });
                  }
                }
                if (oldItem.deleted && !oldItem.tick) {
                  itemMap.set(oldItem.item_id, {...oldItem, tick: false, deleted:true})
                }
              }
            }

            this.orderItems = Array.from(itemMap.values()).sort((a, b) => a.category.localeCompare(b.category));
          },
          {
             deep: true,
             immediate: true
          }
        )
  },
  methods: {
    openPopup: function() {
      if (state.order.state_id === "closed") {
        notify({
          type: "warn",
          text: "A rendelést ma már elküldték",
        });
        return
      } else {
        this.showInitial = true;
      }
    },
    closeOrder: function() {
      for (const item of this.orderItems) {
        if (!item.tick) {
          notify({
            type: "warn",
            text: "Minden sort kikell pipálnod mielött lezárhatod a rendelést.",
          });
          return
        }
      }
      socket.emit("fe_order_closed", {
        date: state.order.date_of_order,
        user_id: this.auth.user.id,
        vendor_id: state.selected_vendor.id
      });
      this.showInitial = false;
      this.showFinish = true;
    },
    doCopyOrder: function() {
      let orderText = ""
      for (const item of this.orderItems) {
        if (item.deleted) {
          continue
        }
        orderText += state.selected_vendor.settings.order_text_template.value
          .replace("${quantity}", item.quantity)
          .replace("${item_name}", item.item_name)
          .replace("${size_name}", item.size_name)
          .replace("\\n", "\n");

        // orderText += `${item.quantity}x ${item.item_name} ${item.size_name}\n`;
        item.tick = true;
      }
      copyText(orderText, undefined, (error, event) =>{
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
    doCopy: function() {
      copyText(this.orderDesc, undefined, (error, event) =>{
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
    }
  }
}
</script>

<style>
.overlay {
    position: fixed;
    width: 100%;
    height: 100%;
    z-index: 1000;
    top: 40%;
    left: 0px;
    opacity: 0.5;
    filter: alpha(opacity=50);
 }
</style>
