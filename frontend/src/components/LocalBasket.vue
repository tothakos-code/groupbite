<template>
  <div class="card">
    <div class="card-header row d-flex justify-content-between p-1">
      <div class="col-2 col-lg-1 my-auto">
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
      </div>
      <div class="col-3 col-lg-4 d-none d-sm-inline d-md-none d-lg-inline text-start my-auto">
        <h2 class="text-nowrap">
          Kosarad
        </h2>
      </div>
      <div class="col-7 col-sm-3 col-md-7 col-lg-5 text-center m-auto">
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
        <span title="A fizetendő összeg még változhat, a rendelést leadó személyek számától.(Szállítási díjat több fele osztjuk)">{{ orderStore.userBasketSum }} Ft</span>
      </div>
    </div>
    <div class="row">
      <div class="list-group pe-0">
        <div
          v-if="auth.isLoggedIn"
          class="row px-0 d-flex card-header m-1 mt-0 border border-2 border-top-0 rounded-bottom rounded-top-0"
        >
          <div class="col-12 d-flex justify-content-evenly">
            <div
              data-bs-toggle="tooltip"
              data-bs-placement="bottom"
              data-bs-trigger="hover"
              title="Töröl mindent a kosaradból"
            >
              <button
                class="btn text-nowrap"
                :class="['btn-outline-' + auth.getUserColor ]"
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
              </button>
            </div>
          </div>
        </div>
        <div
          v-for="(item, index) in orderStore.userBasket"
          :key="index"
          class="list-group-item d-flex justify-content-between"
        >
          <div class="col-2">
            <span
              class="badge rounded-pill border"
              :class="['bg-' + auth.getUserColor, 'border-' + auth.getUserColor, {pulse: itemQuantityPulse}]"
              @animationend="itemQuantityPulse = false"
            >{{ item.quantity }} x</span>
          </div>
          <div class="col-7">
            <span>{{ item.item_name }} ({{ item.size_name }})</span>
          </div>
          <div class="col-2 d-flex justify-content-end">
            <span class="text-nowrap pe-0">{{ item.price }} Ft</span>
          </div>
          <div class="col-1 text-end">
            <button
              type="button"
              title="Törlés"
              class="btn btn-close"
              @click="orderStore.removeItem(item.item_id, item.size_id)"
            />
          </div>
        </div>
        <div
          v-if="orderStore.isUserBasketEmpty"
          class="list-group-item d-flex justify-content-center"
        >
          <div class="d-inline">
            <div v-if="!orderStore.isUserBasketEmpty">
              <span class="me-1">Sikerült választanod</span>
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
            <div v-else>
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
        </div>
      </div>
    </div>
  </div>
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
