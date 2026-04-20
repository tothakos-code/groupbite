<template>
  <v-card
    class="mb-4"
    elevation="2"
  >
    <v-card-title class="bg-primary text-white">
      <v-icon left>
        mdi-cog
      </v-icon>
      Általános beállítások
    </v-card-title>
    <v-card-text class="pa-4">
      <v-row>
        <v-col
          cols="12"
          md="6"
        >
          <v-text-field
            v-model="localSettings.title"
            :label="$t('vendor.settings.title')"
            prepend-icon="mdi-format-title"
            variant="outlined"
            required
            density="comfortable"
          />
        </v-col>
        <v-col
          cols="12"
          md="6"
        >
          <v-text-field
            v-model="localSettings.link"
            :label="$t('vendor.settings.link')"
            prepend-icon="mdi-link"
            variant="outlined"
            density="comfortable"
          />
        </v-col>
      </v-row>

      <v-row>
        <v-col
          cols="12"
          md="6"
        >
          <v-text-field
            v-model="localSettings.comment_example"
            :label="$t('vendor.settings.comment_example')"
            prepend-icon="mdi-comment-text"
            variant="outlined"
            density="comfortable"
          />
        </v-col>
        <v-col
          cols="12"
          md="6"
        >
          <v-text-field
            v-model.number="localSettings.transport_price"
            :label="$t('vendor.settings.transport_price')"
            prepend-icon="mdi-currency-eur"
            :rules="transportPriceRules"
            type="number"
            variant="outlined"
            density="comfortable"
            hint="Rendelés díj (szállítási díj, rendszerhasználat díj, egyebek felszámolása)"
            persistent-hint
          />
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: 'GeneralSettings',
  props: {
    settings: {
      type: Object,
      required: true,
    },
  },
  emits: ['update:settings'],
  data() {
    return {
      // Deep clone so we own the copy and don't mutate the prop directly.
      // Spread ({...this.settings}) would only shallow-copy, leaving nested
      // arrays/objects as shared references.
      localSettings: JSON.parse(JSON.stringify(this.settings)),
      transportPriceRules: [
        (v) =>
          (v !== null && v !== undefined && v !== '') ||
          v === 0 ||
          'Kötelező mező',
        (v) => /^\d+$/.test(v) || 'Csak szám lehetséges',
      ],
    }
  },
  watch: {
    localSettings: {
      deep: true,
      handler(v) {
        this.$emit('update:settings', JSON.parse(JSON.stringify(v))) // deep clone before emitting
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
