<template>
  <v-card
    class="mb-4"
    elevation="2"
  >
    <v-card-title class="bg-primary text-white">
      <v-icon start>
        mdi-puzzle
      </v-icon>
      {{ $t('vendor.plugin.settings') }} ({{ pluginId }})
    </v-card-title>

    <v-card-text class="pa-4">
      <v-alert
        v-if="!hasSettings"
        type="info"
        variant="tonal"
        class="mb-0"
      >
        Ennek a pluginnak nincsenek konfigurálható beállításai.
      </v-alert>

      <v-row v-else>
        <v-col
          v-for="(setting, key) in localSettings"
          :key="key"
          cols="12"
          md="6"
        >
          <v-textarea
            v-if="setting.type === 'STRBOX'"
            v-model="localSettings[key].value"
            :label="$te(setting.labelKey) ? $t(setting.labelKey) : setting.key"
            variant="outlined"
            density="comfortable"
            rows="3"
            auto-grow
          />
          <v-checkbox
            v-else-if="setting.type === 'BOOL'"
            v-model="localSettings[key].value"
            :label="$te(setting.labelKey) ? $t(setting.labelKey) : setting.key"
            density="comfortable"
          />
          <v-text-field
            v-else-if="setting.type === 'INT'"
            v-model.number="localSettings[key].value"
            :label="$te(setting.labelKey) ? $t(setting.labelKey) : setting.key"
            type="number"
            variant="outlined"
            density="comfortable"
          />
          <v-text-field
            v-else
            v-model="localSettings[key].value"
            :label="$te(setting.labelKey) ? $t(setting.labelKey) : setting.key"
            variant="outlined"
            density="comfortable"
          />
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: 'PluginSettings',
  props: {
    settings: {
      type: Object,
      required: true,
    },
    pluginId: {
      type: String,
      required: true,
    },
  },
  emits: ['update:settings'],
  data() {
    return {
      localSettings: JSON.parse(JSON.stringify(this.settings)),
    }
  },
  computed: {
    hasSettings() {
      return Object.keys(this.localSettings).length > 0
    },
  },
  watch: {
    localSettings: {
      deep: true,
      handler(v) {
        this.$emit('update:settings', JSON.parse(JSON.stringify(v)))
      },
    },
    settings: {
      deep: true,
      handler(v) {
        if (JSON.stringify(v) !== JSON.stringify(this.localSettings)) {
          this.localSettings = JSON.parse(JSON.stringify(v))
        }
      },
    },
  },
}
</script>
