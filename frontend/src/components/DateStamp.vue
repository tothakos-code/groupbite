<template>
<div class="col-9 row my-auto flex-fill">
  <div class="col-7 text-center my-auto px-1">
      <span class="text-center text-nowrap px-1">{{ getShownDate }}</span>
  </div>
  <div class="col-5 row d-flex justify-content-between">
    <div class="col-4 p-0">
      <button
        class="btn btn-link p-0"
        :class="['link-' + this.userColor ]"
        :disabled="this.limitToCurrentWeek && this.currentDateSelected.getDay() == 1"
        @click="this.prevDay()"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-caret-left-square" viewBox="0 0 16 16">
          <path d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"/>
          <path d="M10.205 12.456A.5.5 0 0 0 10.5 12V4a.5.5 0 0 0-.832-.374l-4.5 4a.5.5 0 0 0 0 .748l4.5 4a.5.5 0 0 0 .537.082z"/>
        </svg>
      </button>
    </div>
    <div class="col-4 p-0">
      <button
        @click="this.setDay(new Date())"
        class="btn btn-link p-0"
        :class="['link-' + this.userColor ]"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-arrow-counterclockwise" viewBox="0 0 16 16">
          <path d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"/>
          <!-- <path fill-rule="evenodd" d="M8 3a5 5 0 1 1-4.546 2.914.5.5 0 0 0-.908-.417A6 6 0 1 0 8 2v1z"/> -->
          <!-- <path d="M8 4.466V.534a.25.25 0 0 0-.41-.192L5.23 2.308a.25.25 0 0 0 0 .384l2.36 1.966A.25.25 0 0 0 8 4.466z"/> -->
          <path fill-rule="evenodd" d="M 7.9 3.9 a 4 4 90 1 1 -3.6368 2.3312 a 0.4 0.4 90 0 0 -0.7264 -0.3336 A 4.8 4.8 90 1 0 7.9 3.1 v 0.8 z"/>
          <path d="M 8 5.966 V 2.034 a 0.25 0.25 0 0 0 -0.41 -0.192 L 5.23 3.808 a 0.25 0.25 0 0 0 0 0.384 l 2.36 1.966 A 0.25 0.25 0 0 0 8 5.966 z"/>
        </svg>
      </button>
    </div>
    <div class="col-4 p-0">
      <button
        type="button"
        name="button"
        class="btn btn-link p-0"
        :class="['link-' + this.userColor ]"
        :disabled="this.limitToCurrentWeek && this.currentDateSelected.getDay() == 0"
        @click="this.nextDay()"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-caret-right-square" viewBox="0 0 16 16">
          <path d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"/>
          <path d="M5.795 12.456A.5.5 0 0 1 5.5 12V4a.5.5 0 0 1 .832-.374l4.5 4a.5.5 0 0 1 0 .748l-4.5 4a.5.5 0 0 1-.537.082z"/>
        </svg>
      </button>
    </div>
  </div>
</div>
</template>

<script>
import { state } from '@/socket';

export default {
  name: 'DateStamp',
  data() {
    let date = new Date();
    return {
      currentDateSelected: date
    }
  },
  props: {
    'limitToCurrentWeek': Boolean
  },
  emits: ['selectedDate'],
  computed: {
    getShownDate() {
      return this.currentDateSelected.toLocaleDateString('hu-HU', {weekday:'long', month:'short',day:'numeric'});
    },
    getTodayDayDate() {
      return this.currentDateSelected.toLocaleDateString('hu-HU');
    },
    userColor() {
      return state.user.ui_color ? state.user.ui_color : "falusi";
    }
  },
  methods: {
    nextDay: function() {
      if (this.limitToCurrentWeek && this.currentDateSelected.getDay() == 0) {
        return;
      }
      const newDate = new Date(this.currentDateSelected);
      newDate.setDate(newDate.getDate() + 1);
      this.currentDateSelected = newDate;
      this.$emit('selectedDate', this.currentDateSelected);
    },
    prevDay: function() {
      if (this.limitToCurrentWeek && this.currentDateSelected.getDay() == 1) {
        return;
      }
      const newDate = new Date(this.currentDateSelected);
      newDate.setDate(newDate.getDate() - 1);
      this.currentDateSelected = newDate;
      this.$emit('selectedDate', this.currentDateSelected);
    },
    setDay: function(day) {
      this.currentDateSelected = new Date(day);
      this.$emit('selectedDate', this.currentDateSelected);
    }
  }
}
</script>

<style>
</style>
