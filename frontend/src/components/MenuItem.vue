<template>
  <v-list-item
    :title="item.name"
    :subtitle="item.description"
    class="py-0 border-b-sm"
  >
    <v-row
      cols="12"
      class="row m-0 pe-0"
      justify="end"
    >
      <v-col
        v-for="size in item.sizes"
        :key="size.id"
        cols="6"
        sm="4"
        lg="3"
        xl="2"
        xxl="2"
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
      </v-col>
    </v-row>
  </v-list-item>
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
