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
          v-model:active="localSettings.closed_scheduler_active"
          v-model:time="localSettings.closed_scheduler"
          v-model:days="localSettings.closed_scheduler_days"
          :active-label="$t('vendor.settings.closed_scheduler_active')"
          active-icon="mdi-clock-end"
          :time-label="$t('vendor.settings.closed_scheduler')"
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
          v-model:active="localSettings.closure_scheduler_active"
          v-model:time="localSettings.closure_scheduler"
          v-model:days="localSettings.closure_scheduler_days"
          :active-label="$t('vendor.settings.closure_scheduler_active')"
          active-icon="mdi-clock-alert"
          :time-label="$t('vendor.settings.closure_scheduler')"
        />
      </div>

      <v-divider class="my-6" />

      <div class="mb-6">
        <div class="text-body-2 text-medium-emphasis mb-3">
          Menü automatikus szinkronizálás ütemezése. A szinkronizálás a beállított
          időpontban fut és a megadott számú napra előre tölti be a menüt. Hasznos
          ha a forrás API csak bizonyos napokon (pl. hétfő reggel) érhető el a
          következő heti adatokkal.
        </div>
        <DayScheduler
          v-model:active="localSettings.menu_scan_active"
          v-model:time="localSettings.menu_scan_time"
          v-model:days="localSettings.menu_scan_days"
          :active-label="$t('vendor.settings.menu_scan_active')"
          active-icon="mdi-calendar-sync"
          :time-label="$t('vendor.settings.menu_scan_time')"
        />
        <v-row class="mt-3">
          <v-col
            cols="12"
            md="6"
            lg="4"
          >
            <v-text-field
              v-model.number="localSettings.menu_scan_days_ahead"
              :label="$t('vendor.settings.menu_scan_days_ahead')"
              :disabled="!localSettings.menu_scan_active"
              type="number"
              :rules="[(v) => (v >= 1 && v <= 14) || '1 és 14 közötti érték adható meg']"
              prepend-icon="mdi-calendar-range"
              variant="outlined"
              density="comfortable"
              hint="Pl. 7 = egy hétre előre (max. 14)"
              persistent-hint
            />
          </v-col>
        </v-row>
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
              v-model="localSettings.auto_email_order"
              color="success"
              :label="$t('vendor.settings.auto_email_order')"
              :disabled="!smtpStatus || !localSettings.closed_scheduler_active"
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
              v-model.number="localSettings.email_min_user"
              :label="$t('vendor.settings.email_min_user')"
              :disabled="!localSettings.auto_email_order"
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
              v-model="localSettings.order_text_template"
              :label="$t('vendor.settings.order_text_template')"
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
  emits: ['update:settings'],
  data() {
    return {
      // Deep clone so we own the copy and don't mutate the prop directly.
      // Spread ({...this.settings}) would only shallow-copy, leaving nested
      // arrays/objects as shared references.
      localSettings: JSON.parse(JSON.stringify(this.settings)),
      numberRules: [
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
