<template>
  <span
    class="badge p-2 fs-6 bg-secondary align-items-center"
    :class="{
      'bg-success': status === 'collect',
      'bg-warning': status === 'order',
      'bg-danger': status === 'closed'}"
    :title="statusTitle"
    disabled
  >
    {{ statusLabel }}
  </span>
</template>

<script>
import { state } from "@/main";

export default {
  name: 'OrderState',
  computed: {
    status() {
      if (!state.order.state_id) {
        return 'error'
      }
      return state.order.state_id
    },
    statusLabel() {
      if (!state.connected) {
        return 'Kapcsolati probléma'
      }
      switch (state.order.state_id) {
        case 'collect':
          return 'Rendelhetsz'
        case 'order':
          return 'Siess!'
        case 'closed':
          return 'Rendelés elküldve'
        default:
          return 'Töltés...';
      }
    },
    statusTitle() {
      if (!state.connected) {
        return 'Sajnos nem sikerül csatlakozni a szerverhez.'
      }
      switch (state.order.state_id) {
        case 'collect':
          return 'Rendelést még nem küldték el, nyugodtan csatlakozhatsz hozzá.'
        case 'order':
          return 'A rendelés éppen küldés alatt van, ha szeretnél még csatlakozni hozzá SIESS!'
        case 'closed':
          return 'Rendelés elküldve. Sajnos lemaradtál a rendelésről vagy, ha már rendeltél akkor bizosan jólfogsz lakni.'
        default:
          return 'Sajnos valami probléma merült fel a szerveren.';
      }
    }
  }
}
</script>

<style>
</style>
