<template>
  <span>{{ dateStamp }}</span>
</template>

<script>
export default {
  name: 'DateStamp',
  data() {
    return {
      dateStamp: ""
    }
  },
  methods: {
    getToday: function() {
      let today = new Date();
      let todayString = today.toLocaleDateString('hu-HU');
      let todayName = today.toLocaleDateString('hu-HU', {weekday:'long'});
      return todayString + ' - ' + todayName;
    }
  },
  created() {
    this.dateStamp = this.getToday();
  },
}
</script>

<style>
</style>
