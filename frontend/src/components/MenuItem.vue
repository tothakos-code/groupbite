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
        <v-btn
          v-if="size.unlimited || size.quantity > 0"
          class="bg-primary "
          variant="elevated"
          block
          @click="order.addItem(item.id, size.id)"
        >
          <span
            v-if="size.quantity > 0"
            class="text-nowrap me-1"
          >{{ size.quantity }} db</span>
          <span class="text-nowrap me-1">{{ size.name }}</span>
          <span class="text-nowrap">{{ size.price }} Ft</span>
        </v-btn>
        <v-btn
          v-else
          class="text-danger"
          variant="tonal"
          block
          elevation="2"
          :readonly="true"
        >
          <span class="text-nowrap me-1">{{ size.name }}</span>
          Elfogyott
        </v-btn>
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
