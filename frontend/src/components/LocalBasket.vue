<template>
  <v-card class="border-sm">
    <v-card-title class="bg-header border-b-sm p-1">
      <v-row
        class="mx-0 py-1"
        justify="space-between"
      >
        <v-col
          cols="2"
          lg="1"
          class="my-auto"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="28"
            height="28"
            fill="currentColor"
            class="bi bi-basket2 mb-1"
            viewBox="0 0 16 16"
          >
            <path d="M4 10a1 1 0 0 1 2 0v2a1 1 0 0 1-2 0v-2zm3 0a1 1 0 0 1 2 0v2a1 1 0 0 1-2 0v-2zm3 0a1 1 0 1 1 2 0v2a1 1 0 0 1-2 0v-2z" />
            <path d="M5.757 1.071a.5.5 0 0 1 .172.686L3.383 6h9.234L10.07 1.757a.5.5 0 1 1 .858-.514L13.783 6H15.5a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-.623l-1.844 6.456a.75.75 0 0 1-.722.544H3.69a.75.75 0 0 1-.722-.544L1.123 8H.5a.5.5 0 0 1-.5-.5v-1A.5.5 0 0 1 .5 6h1.717L5.07 1.243a.5.5 0 0 1 .686-.172zM2.163 8l1.714 6h8.246l1.714-6H2.163z" />
          </svg>
        </v-col>
        <v-col
          cols="3"
          lg="4"
          class="d-none d-sm-inline d-md-none d-lg-inline text-start my-auto"
        >
          <h2 class="text-nowrap my-auto">
            Kosarad
          </h2>
        </v-col>
        <v-col
          cols="auto"

          class="text-end my-auto"
        >
          <v-tooltip
            location="bottom"
            text="A fizetendő összeg még változhat, a rendelést leadó személyek számától.(Szállítási díjat több fele osztjuk)"
          >
            <template #activator="{ props }">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                fill="currentColor"
                class="bi bi-cash me-1 mb-1"
                viewBox="0 0 16 16"
              >
                <path d="M8 10a2 2 0 1 0 0-4 2 2 0 0 0 0 4z" />
                <path d="M0 4a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H1a1 1 0 0 1-1-1V4zm3 0a2 2 0 0 1-2 2v4a2 2 0 0 1 2 2h10a2 2 0 0 1 2-2V6a2 2 0 0 1-2-2H3z" />
              </svg>
              <span
                v-bind="props"
              >
                {{ orderStore.userBasketSum }} Ft
              </span>
            </template>
          </v-tooltip>
        </v-col>
        <v-col
          v-if="auth.isLoggedIn && !orderStore.isUserBasketEmpty"
          cols="auto"
        >
          <v-tooltip
            location="bottom"
            text="Töröl mindent a kosaradból"
          >
            <template #activator="{ props }">
              <v-btn
                variant="text"
                v-bind="props"
                border="primary thin"
                class=" text-nowrap bg-primary"
                @click="orderStore.clearBasket()"
              >
                <span class="d-none d-sm-inline d-md-none d-xl-inline me-1">Törlés</span>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="20"
                  height="20"
                  fill="currentColor"
                  class="bi bi-trash text-bold"
                  viewBox="0 0 16 16"
                >
                  <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5Zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5Zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6Z" />
                  <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1ZM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118ZM2.5 3h11V2h-11v1Z" />
                </svg>
              </v-btn>
            </template>
          </v-tooltip>
        </v-col>
      </v-row>
    </v-card-title>
    <v-card-text class="p-0">
      <v-row>
        <v-col>
          <v-list class="pt-0 pe-0">
            <template
              v-for="(item, index) in orderStore.userBasket"
              :key="index"
            >
              <v-hover v-slot="{ isHovering, props }">
                <v-list-item

                  :class="isHovering ? 'bg-secondary' : undefined"
                  class="p-0 pe-2 border-b-sm"
                  v-bind="props"
                >
                  <v-row
                    class="m-0 "
                  >
                    <v-col
                      cols="auto"
                      class="d-flex justify-start"
                    >
                      <span
                        class="badge rounded-pill border bg-secondary border-error align-self-center"
                        :class="[{pulse: itemQuantityPulse}]"
                        @animationend="itemQuantityPulse = false"
                      >{{ item.quantity }} x</span>
                    </v-col>
                    <v-col
                      class="flex-grow-1 me-auto"
                      cols="7"
                    >
                      <span>{{ item.item_name }}</span>
                      <span v-if="item.size_name"> ({{ item.size_name }})</span>
                    </v-col>
                    <v-col
                      cols="2"
                      class="d-flex justify-end"
                    >
                      <span class="text-nowrap align-self-center pe-0">{{ item.price }} Ft</span>
                    </v-col>
                  </v-row>
                  <template #append>
                    <button
                      type="button"
                      title="Törlés"
                      class="btn btn-close"
                      @click="orderStore.removeItem(item.item_id, item.size_id)"
                    />
                  </template>
                </v-list-item>
              </v-hover>
            </template>
            <v-list-item
              v-if="orderStore.isUserBasketEmpty"
              class=" d-flex justify-content-center"
            >
              <div class="d-inline">
                <div>
                  <span class="me-1">Üres a kosarad</span>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    fill="currentColor"
                    class="bi bi-basket3 mb-1"
                    viewBox="0 0 16 16"
                  >
                    <path d="M5.757 1.071a.5.5 0 0 1 .172.686L3.383 6h9.234L10.07 1.757a.5.5 0 1 1 .858-.514L13.783 6H15.5a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5H.5a.5.5 0 0 1-.5-.5v-1A.5.5 0 0 1 .5 6h1.717L5.07 1.243a.5.5 0 0 1 .686-.172zM3.394 15l-1.48-6h-.97l1.525 6.426a.75.75 0 0 0 .729.574h9.606a.75.75 0 0 0 .73-.574L15.056 9h-.972l-1.479 6h-9.21z" />
                  </svg>
                </div>
              </div>
            </v-list-item>
          </v-list>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
import { useAuth } from "@/stores/auth";
import { useOrderStore } from "@/stores/order";
import { ref, watch } from "vue";

export default {
  name: "LocalBasket",
  setup() {
    const auth = useAuth();
    const orderStore = useOrderStore();
    const itemQuantityPulse = ref(false);

    watch(() => orderStore.basket, () => {
      itemQuantityPulse.value = true;
    });

    return {
      auth,
      orderStore,
      itemQuantityPulse
    }

  },
}
</script>

<style scoped>
/* styles.css or within a <style> block */
.pulse {
  animation: pulse-animation 0.5s;
}

@keyframes pulse-animation {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

</style>
