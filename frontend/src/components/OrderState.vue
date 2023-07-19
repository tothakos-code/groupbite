<template>
  <div
    class="btn p-3 pe-none btn-secondary"
    :class="{
      'btn-success': this.status === 'collect',
      'btn-warning': this.status === 'order',
      'btn-danger': this.status === 'closed'}">

  </div>
</template>

<script>
import { state } from "@/socket";

export default {
  name: 'OrderState',
  computed: {
    status() {
      return state.orderState
    }
  }
}
</script>

<style>
</style>
