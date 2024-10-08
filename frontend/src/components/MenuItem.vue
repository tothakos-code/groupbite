<template>
  <div class="list-group-item row">
    <div class="row pe-0">
      <div class="col-12 col-lg-6 p-0 text-wrap">
        <span>
          {{ item.name }}
        </span>
      </div>
      <div class="col-12 col-lg-6 p-0">
        <div class="row d-flex flex justify-content-end px-0 mx-0">
          <div
            v-for="size in item.sizes"
            :key="size.id"
            class="row col-6 col-sm-4 col-lg-6 col-xl-4 ms-2 mb-2"
          >
            <button
              v-if="size.quantity !== 0"
              class="btn btn-sm w-100 h-100"
              :class="['btn-' + auth.getUserColor ]"
              @click="order.addItem(item.id, size.id)"
            >
              <span class="text-nowrap me-1">{{ size.name }}</span>
              <span class="text-nowrap">{{ size.price }} Ft</span>
            </button>
            <span
              v-else
              class="btn pe-none btn-outline-danger btn-sm"
            >
              Elfogyott
            </span>
          </div>
        </div>
      </div>
    </div>
    <div
      v-if="item.description"
      class="row"
    >
      <p class="text-body-secondary mb-0 ps-0">
        {{ item.description }}
      </p>
    </div>
  </div>
</template>

<script>
import { useAuth } from "@/stores/auth";
import { useOrderStore } from "@/stores/order";


export default {
  name: "MenuItem",
  props: {
    "item":{
      type: Object,
      default: new Object()
    },
  },
  setup() {
    const auth = useAuth();
    const order = useOrderStore();
    return {
      auth,
      order
    }
  },
}
</script>

<style>
</style>
