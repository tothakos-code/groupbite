<template>
  <div>
    <v-row align="center">
      <v-col
        cols="12"
        md="6"
        lg="4"
      >
        <v-checkbox
          v-model="activeModel"
          color="primary"
          :label="activeLabel"
          :prepend-icon="activeIcon"
          hide-details
        />
      </v-col>
      <v-col
        cols="12"
        md="6"
        lg="4"
      >
        <v-text-field
          v-model="timeModel"
          :label="timeLabel"
          :disabled="!activeModel"
          :rules="getTimeRules(activeModel)"
          prepend-icon="mdi-clock"
          variant="outlined"
          density="comfortable"
          placeholder="HH:MM"
          hide-details="auto"
        />
      </v-col>
    </v-row>

    <v-row class="mt-2">
      <v-col cols="12">
        <div class="d-flex align-center mb-2">
          <v-icon
            size="small"
            class="mr-2"
          >
            mdi-calendar-week
          </v-icon>
          <span class="text-caption font-weight-medium">Napok (üres = minden nap):</span>
          <v-spacer />
          <div class="d-flex flex-wrap gap-1">
            <v-btn
              size="x-small"
              variant="text"
              :disabled="!activeModel"
              @click="daysModel = allDays"
            >
              Összes
            </v-btn>
            <v-btn
              size="x-small"
              variant="text"
              :disabled="!activeModel"
              @click="daysModel = weekdays"
            >
              Hétköznapok
            </v-btn>
            <v-btn
              size="x-small"
              variant="text"
              :disabled="!activeModel"
              @click="daysModel = weekend"
            >
              Hétvége
            </v-btn>
            <v-btn
              size="x-small"
              variant="text"
              color="error"
              :disabled="!activeModel"
              @click="daysModel = []"
            >
              Törlés
            </v-btn>
          </div>
        </div>

        <v-chip-group
          v-model="daysModel"
          :disabled="!activeModel"
          multiple
          column
        >
          <v-chip
            v-for="d in dayOptions"
            :key="d.code"
            :value="d.code"
            filter
            variant="outlined"
            size="small"
          >
            {{ d.label }}
            <span class="text-disabled text-caption ml-1">({{ d.code }})</span>
          </v-chip>
        </v-chip-group>

        <div class="text-caption text-medium-emphasis mt-2">
          Ha nem választasz napot, akkor minden nap fut a megadott időpontban.
        </div>
      </v-col>
    </v-row>
  </div>
</template>

<script>
export default {
  name: 'DayScheduler',
  props: {
    active: {
      type: Boolean,
      required: true,
    },
    time: {
      type: String,
      default: '',
    },
    days: {
      type: Array,
      default: () => [],
    },
    activeLabel: {
      type: String,
      required: true,
    },
    activeIcon: {
      type: String,
      default: 'mdi-clock-end',
    },
    timeLabel: {
      type: String,
      required: true,
    },
  },
  emits: ['update:active', 'update:time', 'update:days'],
  data() {
    return {
      dayOptions: [
        { code: 'mon', label: 'Hétfő' },
        { code: 'tue', label: 'Kedd' },
        { code: 'wed', label: 'Szerda' },
        { code: 'thu', label: 'Csütörtök' },
        { code: 'fri', label: 'Péntek' },
        { code: 'sat', label: 'Szombat' },
        { code: 'sun', label: 'Vasárnap' },
      ],
      allDays: ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
      weekdays: ['mon', 'tue', 'wed', 'thu', 'fri'],
      weekend: ['sat', 'sun'],
    }
  },
  computed: {
    activeModel: {
      get() { return this.active },
      set(val) { this.$emit('update:active', val) },
    },
    timeModel: {
      get() { return this.time },
      set(val) { this.$emit('update:time', val) },
    },
    daysModel: {
      get() { return this.days },
      set(val) { this.$emit('update:days', val) },
    },
  },
  methods: {
    getTimeRules(isActive) {
      return [
        (v) => !isActive || !!v || 'Kötelező mező',
        (v) =>
          !isActive ||
          /^(?:[01]\d|2[0-3]):[0-5]\d$/.test(v) ||
          'Nem megfelelő formátum (HH:MM)',
      ]
    },
  },
}
</script>
