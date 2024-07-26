<template>
  <div class="list-group-item row d-flex ">
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
            @click="basket.addItem(item.id, size.id)"
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
</template>

<script>
import { useAuth } from "@/stores/auth";
import { useBasket } from "@/stores/basket";


export default {
  name: 'MenuItem',
  props: {
    'item':{
      type: Object,
      default: new Object()
    },
  },
  setup() {
    const auth = useAuth();
    const basket = useBasket();
    return {
      auth,
      basket
    }
  },
}
</script>

<style>
</style>
