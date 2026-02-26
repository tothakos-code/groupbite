<template>
  <v-card
    class="mb-4"
    elevation="2"
  >
    <v-card-title class="bg-orange text-white">
      <v-icon left>
        mdi-clock-outline
      </v-icon>
      Rendelés időzítés beállítások
    </v-card-title>
    <v-card-text class="pa-4">
      <!-- Closed Scheduler Section -->
      <div class="mb-6">
        <div class="text-body-2 text-medium-emphasis mb-3">
          A rendelés napi lezárásának időzítése. Beállítható, hogy a hét
          csak bizonos napjain fusson.
        </div>
        <DayScheduler
          v-model:active="settings.closed_scheduler_active.value"
          v-model:time="settings.closed_scheduler.value"
          v-model:days="settings.closed_scheduler_days.value"
          :active-label="settings.closed_scheduler_active.name"
          active-icon="mdi-clock-end"
          :time-label="settings.closed_scheduler.name"
        />
      </div>

      <v-divider class="my-6" />

      <!-- Closure Scheduler Section -->
      <div class="mb-6">
        <div class="text-body-2 text-medium-emphasis mb-3">
          Rendelés léptetése 'Siess' státuszba. Egy rendelés zárásának
          figyelmeztetésének is lehet használni. Beállítható, hogy a hét
          csak bizonos napjain fusson.
        </div>
        <DayScheduler
          v-model:active="settings.closure_scheduler_active.value"
          v-model:time="settings.closure_scheduler.value"
          v-model:days="settings.closure_scheduler_days.value"
          :active-label="settings.closure_scheduler_active.name"
          active-icon="mdi-clock-alert"
          :time-label="settings.closure_scheduler.name"
        />
      </div>

      <v-divider class="my-6" />

      <!-- SMTP Warning Alert -->
      <v-alert
        v-if="!smtpStatus"
        type="warning"
        variant="tonal"
        class="mb-6"
      >
        <template #prepend>
          <v-icon>mdi-alert</v-icon>
        </template>
        SMTP beállítások nem konfiguráltak. Az automatikus email funkciók
        nem elérhetők.
      </v-alert>

      <!-- Auto Email Order Section -->
      <div class="mb-6">
        <div class="text-body-2 text-medium-emphasis mb-3">
          Rendelés zárás időzíő kor a rendelés tételei emailben elküldése
          a beállított email címre. Ehhez egy minimum rendelésben részvevő
          felhasználó feltételt is lehet adni így csak akkor megy ki az
          email ha minimum ennyi felhasználó rendel.
        </div>

        <v-row align="center">
          <v-col
            cols="12"
            md="6"
            lg="4"
          >
            <v-checkbox
              v-model="settings.auto_email_order.value"
              color="success"
              :label="settings.auto_email_order.name"
              :disabled="!smtpStatus || !settings.closed_scheduler_active.value"
              prepend-icon="mdi-email-fast"
              hide-details
            />
          </v-col>
          <v-col
            cols="12"
            md="6"
            lg="4"
          >
            <v-text-field
              v-model.number="settings.email_min_user.value"
              :label="settings.email_min_user.name"
              :disabled="!settings.auto_email_order.value"
              :rules="numberRules"
              type="number"
              prepend-icon="mdi-account-multiple"
              variant="outlined"
              density="comfortable"
              hint="Minimum résztvevő szám a rendelés elküldéséhez"
              persistent-hint
            />
          </v-col>
        </v-row>
      </div>

      <v-divider class="my-6" />

      <!-- Order Text Template Section -->
      <div>
        <div class="text-body-2 text-medium-emphasis mb-3">
          Ez a minta alapján jelennek meg a sorok az emailben és/vagy
          manuálisan vágólapra másolva rendelés tételei.
        </div>
        <v-row>
          <v-col cols="12">
            <v-textarea
              v-model="settings.order_text_template.value"
              :label="settings.order_text_template.name"
              prepend-icon="mdi-text-box"
              variant="outlined"
              rows="3"
              auto-grow
              hint="Használható változók: ${quantity}, ${item_name}, ${size_name}"
              persistent-hint
            />
          </v-col>
        </v-row>
      </div>
    </v-card-text>
  </v-card>
</template>

<script>
import DayScheduler from './DayScheduler.vue'

export default {
  name: 'OrderTimingSettings',
  components: { DayScheduler },
  props: {
    settings: {
      type: Object,
      required: true,
    },
    smtpStatus: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      numberRules: [
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
