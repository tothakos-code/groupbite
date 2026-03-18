<template>
  <v-card
    class="mb-4"
    elevation="2"
  >
    <v-card-title class="bg-secondary text-white">
      <v-icon left>
        mdi-palette
      </v-icon>
      Felhasználói felület beállítások
    </v-card-title>
    <v-card-text class="pa-4">
      <v-checkbox
        v-model="localSettings.show_notification_button"
        color="primary"
        :label="$t('vendor.settings.show_notification_button')"
        prepend-icon="mdi-bell"
        hide-details
      />
      <v-checkbox
        v-model="localSettings.show_favourites"
        color="primary"
        :label="$t('vendor.settings.show_favourites')"
        prepend-icon="mdi-star"
        hide-details
      />
    </v-card-text>
    <v-divider class="my-4" />
    Rendelés opciók engedélyezése
    <v-row class="pa-4">
      <v-col
        cols="12"
        md="4"
      >
        <v-checkbox
          v-model="localSettings.enable_full_automatic_order"
          color="success"
          :label="$t('vendor.settings.enable_full_automatic_order')"
          prepend-icon="mdi-robot"
          hide-details
        />
      </v-col>
      <v-col
        cols="12"
        md="4"
      >
        <v-checkbox
          v-model="localSettings.enable_email_order"
          color="info"
          :label="$t('vendor.settings.enable_email_order')"
          prepend-icon="mdi-email"
          hide-details
        />
      </v-col>
      <v-col
        cols="12"
        md="4"
      >
        <v-checkbox
          v-model="localSettings.enable_manual_order"
          color="warning"
          :label="$t('vendor.settings.enable_manual_order')"
          prepend-icon="mdi-hand-back-right"
          hide-details
        />
      </v-col>
    </v-row>
  </v-card>
</template>

<script>
export default {
  name: 'UiSettings',
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
