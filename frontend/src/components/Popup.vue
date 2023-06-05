<template>
  <!-- <Teleport to="body"> -->
    <div class="popup">
      <div class="popup-inner">
        <h2>{{ title }}</h2>
        <slot></slot>
        <br>
        <button class="btn btn-secondary" @click="$emit('confirm')">Confirm</button>
        <button class="btn btn-secondary" @click="$emit('cancel')">Cancel</button>
      </div>
    </div>
  <!-- </Teleport> -->
</template>

<script>
export default {
  name: 'PopupWrapper',
  // data() {
  //   return {
  //     show: false,
  //     title: this.title
  //   }
  // },
  props: {
    title: String,
  },
  emits: ['cancel', 'confirm']
  // methods: {
  //   close: function() {
  //     let today = new Date();
  //     let todayString = today.toLocaleDateString('hu-HU');
  //     let todayName = today.toLocaleDateString('hu-HU', {weekday:'long'});
  //     return todayString + ' - ' + todayName;
  //   }
  // },
  // created() {
  //   this.dateStamp = this.getToday();
  // },
}
</script>

<style>
</style>
