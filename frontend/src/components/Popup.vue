<template>
    <div class="popup">
      <div class="popup-inner">
        <h2>{{ title }}</h2>
        <slot></slot>
        <br>
        <br>
        <button class="btn btn-secondary" @click="$emit('confirm')">Confirm</button>
        <button class="btn btn-secondary" @click="$emit('cancel')">Cancel</button>
      </div>
    </div>
</template>

<script>
export default {
  name: 'PopupWrapper',
  props: {
    title: String,
  },
  emits: ['cancel', 'confirm']
}
</script>

<style>
</style>
