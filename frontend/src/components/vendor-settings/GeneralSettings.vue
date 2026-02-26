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
            v-model="settings.title.value"
            :label="settings.title.name"
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
            v-model="settings.link.value"
            :label="settings.link.name"
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
            v-model="settings.comment_example.value"
            :label="settings.comment_example.name"
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
            v-model.number="settings.transport_price.value"
            :label="settings.transport_price.name"
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
  data() {
    return {
      transportPriceRules: [
        (v) =>
          (v !== null && v !== undefined && v !== '') ||
          v === 0 ||
          'Kötelező mező',
        (v) => /^\d+$/.test(v) || 'Csak szám lehetséges',
      ],
    }
  },
}
</script>
