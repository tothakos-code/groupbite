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
        v-model="settings.show_notification_button"
        color="primary"
        :label="$t('vendor.settings.show_notification_button')"
        prepend-icon="mdi-bell"
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
          v-model="settings.enable_full_automatic_order"
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
          v-model="settings.enable_email_order"
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
          v-model="settings.enable_manual_order"
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
}
</script>
