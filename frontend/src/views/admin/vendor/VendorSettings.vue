<template>
  <div class="row ms-2">
    <v-container
      v-if="!isLoading"
      max-width="1400"
    >
      <v-form ref="form">
        <!-- General Settings -->
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
                  v-model="vendor.settings.title.value"
                  :label="vendor.settings.title.name"
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
                  v-model="vendor.settings.link.value"
                  :label="vendor.settings.link.name"
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
                  v-model="vendor.settings.comment_example.value"
                  :label="vendor.settings.comment_example.name"
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
                  v-model.number="vendor.settings.transport_price.value"
                  :label="vendor.settings.transport_price.name"
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

        <!-- UI Settings -->
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
              v-model="vendor.settings.show_notification_button.value"
              color="primary"
              label="Értesítési gomb megjelenítése"
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
                v-model="vendor.settings.enable_full_automatic_order.value"
                color="success"
                label="Teljes automatikus rendelés"
                prepend-icon="mdi-robot"
                hide-details
              />
            </v-col>
            <v-col
              cols="12"
              md="4"
            >
              <v-checkbox
                v-model="vendor.settings.enable_email_order.value"
                color="info"
                label="Email rendelés"
                prepend-icon="mdi-email"
                hide-details
              />
            </v-col>
            <v-col
              cols="12"
              md="4"
            >
              <v-checkbox
                v-model="vendor.settings.enable_manual_order.value"
                color="warning"
                label="Manuális rendelés"
                prepend-icon="mdi-hand-back-right"
                hide-details
              />
            </v-col>
          </v-row>
        </v-card>

        <!-- Order Process Settings -->
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
                A rendelés napi lezárásának időzítése. Beállítható, hogy a hét csak bizonos napjain fusson.
              </div>

              <v-row align="center">
                <v-col
                  cols="12"
                  md="6"
                  lg="4"
                >
                  <v-checkbox
                    v-model="vendor.settings.closed_scheduler_active.value"
                    color="primary"
                    :label="vendor.settings.closed_scheduler_active.name"
                    prepend-icon="mdi-clock-end"
                    hide-details
                  />
                </v-col>
                <v-col
                  cols="12"
                  md="6"
                  lg="4"
                >
                  <v-text-field
                    v-model="vendor.settings.closed_scheduler.value"
                    :label="vendor.settings.closed_scheduler.name"
                    :disabled="!vendor.settings.closed_scheduler_active.value"
                    :rules="getTimeRules(vendor.settings.closed_scheduler_active.value)"
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

                    <!-- Quick actions -->
                    <div class="d-flex flex-wrap gap-1">
                      <v-btn
                        size="x-small"
                        variant="text"
                        :disabled="!vendor.settings.closed_scheduler_active.value"
                        @click="vendor.settings.closed_scheduler_days.value = ['mon','tue','wed','thu','fri','sat','sun']"
                      >
                        Összes
                      </v-btn>
                      <v-btn
                        size="x-small"
                        variant="text"
                        :disabled="!vendor.settings.closed_scheduler_active.value"
                        @click="vendor.settings.closed_scheduler_days.value = ['mon','tue','wed','thu','fri']"
                      >
                        Hétköznapok
                      </v-btn>
                      <v-btn
                        size="x-small"
                        variant="text"
                        :disabled="!vendor.settings.closed_scheduler_active.value"
                        @click="vendor.settings.closed_scheduler_days.value = ['sat','sun']"
                      >
                        Hétvége
                      </v-btn>
                      <v-btn
                        size="x-small"
                        variant="text"
                        color="error"
                        :disabled="!vendor.settings.closed_scheduler_active.value"
                        @click="vendor.settings.closed_scheduler_days.value = []"
                      >
                        Törlés
                      </v-btn>
                    </div>
                  </div>

                  <v-chip-group
                    v-model="vendor.settings.closed_scheduler_days.value"
                    :disabled="!vendor.settings.closed_scheduler_active.value"
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

            <v-divider class="my-6" />

            <!-- Closure Scheduler Section -->
            <div class="mb-6">
              <div class="text-body-2 text-medium-emphasis mb-3">
                Rendelés léptetése 'Siess' státuszba. Egy rendelés zárásának figyelmeztetésének is lehet használni. Beállítható, hogy a hét csak bizonos napjain fusson.
              </div>

              <v-row align="center">
                <v-col
                  cols="12"
                  md="6"
                  lg="4"
                >
                  <v-checkbox
                    v-model="vendor.settings.closure_scheduler_active.value"
                    color="primary"
                    :label="vendor.settings.closure_scheduler_active.name"
                    prepend-icon="mdi-clock-alert"
                    hide-details
                  />
                </v-col>
                <v-col
                  cols="12"
                  md="6"
                  lg="4"
                >
                  <v-text-field
                    v-model="vendor.settings.closure_scheduler.value"
                    :label="vendor.settings.closure_scheduler.name"
                    :disabled="!vendor.settings.closure_scheduler_active.value"
                    :rules="getTimeRules(vendor.settings.closure_scheduler_active.value)"
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

                    <!-- Quick actions -->
                    <div class="d-flex flex-wrap gap-1">
                      <v-btn
                        size="x-small"
                        variant="text"
                        :disabled="!vendor.settings.closure_scheduler_active.value"
                        @click="vendor.settings.closure_scheduler_days.value = ['mon','tue','wed','thu','fri','sat','sun']"
                      >
                        Összes
                      </v-btn>
                      <v-btn
                        size="x-small"
                        variant="text"
                        :disabled="!vendor.settings.closure_scheduler_active.value"
                        @click="vendor.settings.closure_scheduler_days.value = ['mon','tue','wed','thu','fri']"
                      >
                        Hétköznapok
                      </v-btn>
                      <v-btn
                        size="x-small"
                        variant="text"
                        :disabled="!vendor.settings.closure_scheduler_active.value"
                        @click="vendor.settings.closure_scheduler_days.value = ['sat','sun']"
                      >
                        Hétvége
                      </v-btn>
                      <v-btn
                        size="x-small"
                        variant="text"
                        color="error"
                        :disabled="!vendor.settings.closure_scheduler_active.value"
                        @click="vendor.settings.closure_scheduler_days.value = []"
                      >
                        Törlés
                      </v-btn>
                    </div>
                  </div>

                  <v-chip-group
                    v-model="vendor.settings.closure_scheduler_days.value"
                    :disabled="!vendor.settings.closure_scheduler_active.value"
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
              SMTP beállítások nem konfiguráltak. Az automatikus email funkciók nem elérhetők.
            </v-alert>

            <!-- Auto Email Order Section -->
            <div class="mb-6">
              <div class="text-body-2 text-medium-emphasis mb-3">
                Rendelés zárás időzíő kor a rendelés tételei emailben elküldése a beállított email címre. Ehhez egy minimum rendelésben részvevő felhasználó feltételt is lehet adni így csak akkor megy ki az email ha minimum ennyi felhasználó rendel.
              </div>

              <v-row align="center">
                <v-col
                  cols="12"
                  md="6"
                  lg="4"
                >
                  <v-checkbox
                    v-model="vendor.settings.auto_email_order.value"
                    color="success"
                    :label="vendor.settings.auto_email_order.name"
                    :disabled="!smtpStatus || !vendor.settings.closed_scheduler_active.value"
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
                    v-model.number="vendor.settings.email_min_user.value"
                    :label="vendor.settings.email_min_user.name"
                    :disabled="!vendor.settings.auto_email_order.value"
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
                Ez a minta alapján jelennek meg a sorok az emailben és/vagy manuálisan vágólapra másolva rendelés tételei.
              </div>

              <v-row>
                <v-col cols="12">
                  <v-textarea
                    v-model="vendor.settings.order_text_template.value"
                    :label="vendor.settings.order_text_template.name"
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

        <!-- Automatic Email Order Settings -->
        <v-card
          class="mb-4"
          elevation="2"
        >
          <v-card-title class="bg-success text-white">
            <v-icon left>
              mdi-email-fast
            </v-icon>
            Automatikus email rendelés beállítások
          </v-card-title>
          <v-card-text class="pa-4">
            <v-expand-transition>
              <div v-if="vendor.settings.auto_email_order.value">
                <v-divider class="my-4" />

                <v-row>
                  <v-col
                    cols="12"
                    md="6"
                  >
                    <v-combobox
                      v-model="vendor.settings.auto_email_order_to.value"
                      chips
                      multiple
                      :label="vendor.settings.auto_email_order_to.name"
                      :rules="[v => validateEmails(v, true)]"
                      prepend-icon="mdi-email-outline"
                      variant="outlined"
                      density="comfortable"
                      closable-chips
                    >
                      <template #chip="{ props, item }">
                        <v-chip
                          v-bind="props"
                          :text="item.raw"
                          closable
                          size="small"
                        />
                      </template>
                    </v-combobox>
                  </v-col>
                  <v-col
                    cols="12"
                    md="6"
                  >
                    <v-combobox
                      v-model="vendor.settings.auto_email_order_cc.value"
                      chips
                      multiple
                      :label="vendor.settings.auto_email_order_cc.name"
                      :rules="[validateEmails]"
                      prepend-icon="mdi-email-multiple-outline"
                      variant="outlined"
                      density="comfortable"
                      closable-chips
                    >
                      <template #chip="{ props, item }">
                        <v-chip
                          v-bind="props"
                          :text="item.raw"
                          closable
                          size="small"
                        />
                      </template>
                    </v-combobox>
                  </v-col>
                </v-row>

                <v-row>
                  <v-col cols="12">
                    <v-text-field
                      v-model="vendor.settings.auto_email_subject.value"
                      :label="vendor.settings.auto_email_subject.name"
                      prepend-icon="mdi-format-title"
                      variant="outlined"
                      density="comfortable"
                    />
                  </v-col>
                </v-row>

                <v-row>
                  <v-col cols="12">
                    <v-textarea
                      v-model="vendor.settings.auto_email_order_template.value"
                      :label="vendor.settings.auto_email_order_template.name"
                      prepend-icon="mdi-file-document-edit"
                      variant="outlined"
                      rows="4"
                      auto-grow
                      class="code-textarea"
                    />
                  </v-col>
                </v-row>
              </div>
            </v-expand-transition>
          </v-card-text>
        </v-card>

        <WebhookSettings :vendor-id="vendor.id" />

        <!-- Action Buttons -->
        <v-card elevation="2">
          <v-card-actions class="pa-4">
            <v-btn
              color="primary"
              size="large"
              prepend-icon="mdi-content-save"
              :loading="saving"
              @click="saveSettings"
            >
              Mentés
            </v-btn>
            <v-spacer />
            <v-btn
              color="secondary"
              variant="outlined"
              prepend-icon="mdi-refresh"
              @click="resetForm"
            >
              Visszaállítás
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-form>
    </v-container>

    <!-- Loading State -->
    <v-container v-else>
      <v-row justify="center">
        <v-col cols="auto">
          <v-progress-circular
            indeterminate
            color="primary"
            size="64"
          />
          <p class="text-center mt-4">
            Beállítások betöltése...
          </p>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import { useVendorStore } from "@/stores/vendor";
import { useAuth } from "@/stores/auth";
import { ref } from 'vue';
import axios from "axios";
import WebhookSettings from "@/components/vendor/WebhookSettings.vue"

export default {
  name: "VendorSettings",
  components: {
    WebhookSettings
  },
  setup() {
    const auth = useAuth();
    const vendorStore = useVendorStore();
    const form = ref();

    return {
      auth,
      vendorStore,
      form
    };
  },
  data() {
    return {
      vendor: {},
      originalVendor: {},
      isLoading: true,
      saving: false,
      smtpStatus: false,
      transportPriceRules: [
        v => (v !== null && v !== undefined && v !== '') || v === 0 || 'Kötelező mező',
        v => /^\d+$/.test(v) || 'Csak szám lehetséges'
      ],
      numberRules: [
        v => (v !== null && v !== undefined && v !== '') || v === 0 || 'Kötelező mező',
        v => /^\d+$/.test(v) || 'Csak szám lehetséges'
      ],
      dayOptions: [
        { code: 'mon', label: 'Hétfő' },
        { code: 'tue', label: 'Kedd' },
        { code: 'wed', label: 'Szerda' },
        { code: 'thu', label: 'Csütörtök' },
        { code: 'fri', label: 'Péntek' },
        { code: 'sat', label: 'Szombat' },
        { code: 'sun', label: 'Vasárnap' },
      ],
    };
  },
  mounted() {
    this.getSettings();
  },
  methods: {
    async getSettings() {
      try {
        this.isLoading = true;

        // Fetch vendor settings
        const response = await this.vendorStore.fetchVendor(this.$route.params.id);
        this.vendor = response.data.data;

        // Initialize new settings with default values if they don't exist
        this.initializeNewSettings();

        // Store original state for reset functionality
        this.originalVendor = JSON.parse(JSON.stringify(this.vendor));

        // Check SMTP status
        await this.checkSmtpStatus();

      } catch (error) {
        console.error('Error loading settings:', error);
        this.$toast?.error('Hiba a beállítások betöltése során');
      } finally {
        this.isLoading = false;
      }
    },

    initializeNewSettings() {
      // Initialize new settings if they don't exist
      const newSettings = {
        enable_full_automatic_order: { name: 'Teljes automatikus rendelés engedélyezése', value: false },
        enable_email_order: { name: 'Email rendelés engedélyezése', value: false },
        enable_manual_order: { name: 'Manuális rendelés engedélyezése', value: true },
        show_notification_button: { name: 'Értesítési gomb megjelenítése', value: true }
      };

      Object.keys(newSettings).forEach(key => {
        if (!this.vendor.settings[key]) {
          this.vendor.settings[key] = newSettings[key];
        }
      });
    },

    async checkSmtpStatus() {
      try {
        const response = await axios.get(`/api/setting/get/smtp_address`);
        this.smtpStatus = response.status === 200 && response.data.smtp_address !== "";
      } catch (error) {
        console.error('Error checking SMTP status:', error);
        this.smtpStatus = false;
      }
    },

    async saveSettings() {
      try {
        const { valid } = await this.$refs.form.validate();

        if (!valid) {
          this.$toast?.error('Kérjük javítsa ki a hibákat a mentés előtt');
          return;
        }

        this.saving = true;

        await this.vendorStore.saveSettings(
          this.$route.params.id,
          this.vendor.settings
        );

        this.$toast?.success('Beállítások sikeresen mentve');

        // Update original state after successful save
        this.originalVendor = JSON.parse(JSON.stringify(this.vendor));

      } catch (error) {
        console.error('Error saving settings:', error);
        this.$toast?.error('Hiba a beállítások mentése során');
      } finally {
        this.saving = false;
      }
    },

    resetForm() {
      this.vendor = JSON.parse(JSON.stringify(this.originalVendor));
      this.$refs.form.resetValidation();
    },

    getTimeRules(isActive) {
      return [
        v => !isActive || !!v || 'Kötelező mező',
        v => !isActive || /^(?:[01]\d|2[0-3]):[0-5]\d$/.test(v) || 'Nem megfelelő formátum (HH:MM)'
      ];
    },

    validateEmails(value, required = false) {
      if (required && (!value || value.length === 0)) {
        return "Legalább egy email cím szükséges.";
      }

      if (!value || value.length === 0) {
        return true;
      }

      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      const invalidEmails = value.filter(email => !emailPattern.test(email));

      if (invalidEmails.length > 0) {
        return `Érvénytelen email címek: ${invalidEmails.join(", ")}`;
      }

      return true;
    }
  }
};
</script>

<style scoped>
.v-card-title {
  font-weight: 600;
  letter-spacing: 0.5px;
}

.v-progress-circular {
  margin: 2rem auto;
}

.v-alert {
  border-radius: 8px;
}

.v-chip {
  margin: 2px;
}

.v-expansion-panel-text {
  padding: 0;
}

.code-textarea {
  font-family: "JetBrains Mono", "Fira Code", monospace;
  font-size: 13px;
  line-height: 1.5;
}
</style>
