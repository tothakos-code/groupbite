<template>
  <div class="row d-flex justify-content-center align-items-center">
    <div class="col text-end">
      <button type="button" name="button" class="btn btn-link" :disabled="this.currentDate.getDay() == 1" @click="this.prevDay()">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-caret-left-square" viewBox="0 0 16 16">
          <path d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"/>
          <path d="M10.205 12.456A.5.5 0 0 0 10.5 12V4a.5.5 0 0 0-.832-.374l-4.5 4a.5.5 0 0 0 0 .748l4.5 4a.5.5 0 0 0 .537.082z"/>
        </svg>
      </button>
    </div>
    <div class="col">
      <span class="row justify-content-center">{{ getTodayDayDate }}</span>
      <span class="row justify-content-center">{{ getTodayDayName }}</span>
    </div>
    <div class="col text-start">
      <button type="button" name="button" class="btn btn-link" :disabled="this.currentDate.getDay() == 0" @click="this.nextDay()">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-caret-right-square" viewBox="0 0 16 16">
          <path d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"/>
          <path d="M5.795 12.456A.5.5 0 0 1 5.5 12V4a.5.5 0 0 1 .832-.374l4.5 4a.5.5 0 0 1 0 .748l-4.5 4a.5.5 0 0 1-.537.082z"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DateStamp',
  data() {
    return {
      currentDate: new Date()
    }
  },
  emits: ['selectedDate'],
  computed: {
    getTodayDayName() {
      return this.currentDate.toLocaleDateString('hu-HU', {weekday:'long'});
    },
    getTodayDayDate() {
      return this.currentDate.toLocaleDateString('hu-HU');
    }
  },
  methods: {
    nextDay: function() {
      if (this.currentDate.getDay() == 0) {
        return;
      }
      const newDate = new Date(this.currentDate);
      newDate.setDate(newDate.getDate() + 1);
      this.currentDate = newDate;
      this.$emit('selectedDate', this.currentDate.getDay());
    },
    prevDay: function() {
      if (this.currentDate.getDay() == 1) {
        return;
      }
      const newDate = new Date(this.currentDate);
      newDate.setDate(newDate.getDate() - 1);
      this.currentDate = newDate;
      this.$emit('selectedDate', this.currentDate.getDay());
    }
  }
}
</script>

<style>
</style>
