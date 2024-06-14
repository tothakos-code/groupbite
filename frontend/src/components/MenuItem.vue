<template>
  <div class="list-group-item row d-flex ">
    <div class="col-12 col-lg-8 p-0">
      <span>
        {{ item.name }}
      </span>
    </div>
    <div class="col-12 col-lg-4 p-0 flex-wrap">
      <div class="d-flex justify-content-end">
        <!-- <span
          v-if="item.sold_out"
          class="btn pe-none btn-outline-danger btn-sm"
        >Elfogyott</span> -->
        <button
          v-for="size in item.sizes"
          :key="size.id"
          class="btn btn-sm col-6 col-sm-6 ms-2"
          :class="['btn-' + auth.getUserColor ]"
          @click="basket.addItem(size.id)"
        >
          <span class="text-nowrap me-1">{{ size.size }}</span>
          <span class="text-nowrap">{{ size.price }} Ft</span>
        </button>
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
