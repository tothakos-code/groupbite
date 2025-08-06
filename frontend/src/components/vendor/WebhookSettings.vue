<template>
  <v-card
    class="mb-4"
    elevation="2"
  >
    <v-card-title class="bg-orange text-white py-3">
      <v-icon left>
        mdi-webhook
      </v-icon>
      Webhook beállítások
    </v-card-title>

    <v-card-text class="pa-4">
      <!-- Existing webhooks -->
      <div
        v-for="(webhook, index) in webhooks"
        :key="webhook.id"
        class="mb-4"
      >
        <v-card
          variant="outlined"
          class="mb-3"
        >
          <v-card-title class="d-flex align-center justify-space-between pa-3 bg-grey-lighten-5">
            <div class="d-flex align-center">
              <v-icon
                class="mr-2"
                size="small"
              >
                mdi-webhook
              </v-icon>
              <span class="text-body-1">Webhook #{{ index + 1 }}</span>
            </div>
            <div class="d-flex align-center ga-2">
              <v-switch
                v-model="webhook.is_active"
                color="primary"
                density="compact"
                hide-details
                inset
              >
                <template #label>
                  <span class="text-caption">Aktív</span>
                </template>
              </v-switch>
              <v-btn
                color="success"
                variant="test"
                icon="mdi-content-save"
                size="small"
                title="Webhook mentése"
                @click="saveWebhook(index)"
              />
              <v-btn
                icon="mdi-test-tube"
                size="small"
                variant="text"
                color="warning"
                title="Webhook tesztelése"
                @click="testWebhook(index)"
              />
              <v-btn
                icon="mdi-delete"
                size="small"
                variant="text"
                color="error"
                title="Webhook törlése"
                @click="removeWebhook(webhook.id)"
              />
            </div>
          </v-card-title>

          <v-card-text class="pa-3">
            <!-- Form reference for validation -->
            <v-form ref="webhookForm">
              <!-- URL and message_template in one row -->
              <v-row dense>
                <v-col
                  cols="12"
                  md="8"
                >
                  <v-text-field
                    v-model="webhook.url"
                    label="Webhook URL"
                    :rules="urlRules"
                    prepend-icon="mdi-link"
                    variant="outlined"
                    density="compact"
                    placeholder="https://example.com/webhook"
                  />
                </v-col>
                <v-col
                  cols="12"
                  md="4"
                >
                  <v-textarea
                    v-model="webhook.message_template"
                    label="Üzenet sablon"
                    prepend-icon="mdi-message-text"
                    variant="outlined"
                    density="compact"
                    rows="2"
                    auto-grow
                    placeholder="Webhook üzenet..."
                  />
                </v-col>
              </v-row>

              <!-- Trigger settings in one row -->
              <v-row dense>
                <v-col
                  cols="12"
                  md="3"
                >
                  <v-radio-group
                    v-model="webhook.trigger_type"
                    density="compact"
                    hide-details
                  >
                    <template #label>
                      <div class="d-flex align-center">
                        <v-icon
                          size="small"
                          class="mr-1"
                        >
                          mdi-lightning-bolt
                        </v-icon>
                        <span class="text-caption">Trigger típusa:</span>
                      </div>
                    </template>
                    <v-radio
                      label="Időzített"
                      value="time"
                      density="compact"
                    >
                      <template #label>
                        <div class="d-flex align-center">
                          <v-icon
                            size="small"
                            class="mr-1"
                          >
                            mdi-clock
                          </v-icon>
                          <span class="text-body-2">Időzített</span>
                        </div>
                      </template>
                    </v-radio>
                    <v-radio
                      label="Esemény alapú"
                      value="event"
                      density="compact"
                    >
                      <template #label>
                        <div class="d-flex align-center">
                          <v-icon
                            size="small"
                            class="mr-1"
                          >
                            mdi-calendar-alert
                          </v-icon>
                          <span class="text-body-2">Esemény alapú</span>
                        </div>
                      </template>
                    </v-radio>
                  </v-radio-group>
                </v-col>

                <!-- Time trigger settings -->
                <v-col
                  v-if="webhook.trigger_type === 'time'"
                  cols="12"
                  md="3"
                >
                  <v-text-field
                    v-model="webhook.scheduled_time"
                    label="Időpont"
                    :rules="timeRules"
                    prepend-icon="mdi-clock"
                    variant="outlined"
                    density="compact"
                    placeholder="HH:MM"
                  />
                </v-col>

                <!-- Event trigger settings -->
                <v-col
                  v-if="webhook.trigger_type === 'event'"
                  cols="12"
                  md="6"
                >
                  <v-select
                    v-model="webhook.event_types"
                    :items="eventOptions"
                    label="Események"
                    :rules="eventRules"
                    prepend-icon="mdi-calendar-alert"
                    variant="outlined"
                    density="compact"
                    multiple
                    chips
                    closable-chips
                  />
                </v-col>
              </v-row>

              <!-- Retry settings (only if enabled) -->
              <v-row
                v-if="webhook.retryEnabled"
                dense
              >
                <v-col
                  cols="12"
                  md="6"
                >
                  <v-text-field
                    v-model.number="webhook.retryCount"
                    label="Újrapróbálkozások száma"
                    type="number"
                    min="1"
                    max="10"
                    prepend-icon="mdi-counter"
                    variant="outlined"
                    density="compact"
                  />
                </v-col>
                <v-col
                  cols="12"
                  md="6"
                >
                  <v-text-field
                    v-model.number="webhook.retryDelay"
                    label="Várakozási idő (másodperc)"
                    type="number"
                    min="1"
                    max="3600"
                    prepend-icon="mdi-timer"
                    variant="outlined"
                    density="compact"
                  />
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>
        </v-card>
      </div>

      <!-- Action buttons section - Improved styling -->
      <v-card
        variant="outlined"
        class="mt-4"
      >
        <v-card-text class="pa-3">
          <div class="d-flex justify-center">
            <v-btn
              color="primary"
              variant="elevated"
              prepend-icon="mdi-plus"
              size="default"
              class="px-6"
              @click="addWebhook"
            >
              Új webhook hozzáadása
            </v-btn>
          </div>
        </v-card-text>
      </v-card>
    </v-card-text>
  </v-card>
</template>

<script>
import { useVendorStore } from "@/stores/vendor";
import { useWebhookStore } from "@/stores/webhook";

export default {
  name: 'WebhookSettings',
  props: {
    vendorId: {
      type: String,
      required: true
    }
  },
  setup() {
    const vendorStore = useVendorStore();
    const webhookStore = useWebhookStore();
    return {
      vendorStore,
      webhookStore
    }
  },
  data() {
    return {
      isLoading: true,
      webhooks: [],
      eventOptions: [
        { title: 'Rendelés küldés státusz után', value: 'afterClose' },
        { title: 'Rendelés küldés státusz előtt', value: 'beforeClose' },
        { title: 'Rendeléshez Item hozzáadás után', value: 'afterAdd' },
        { title: 'Rendeléshez Item hozzáadás előtt', value: 'beforeAdd' },
        { title: 'Rendeléshez Item törlés után', value: 'afterRemove' },
        { title: 'Rendeléshez Item törlés előtt', value: 'beforeRemove' },
        { title: 'Rendelés létrehozás után', value: 'afterCollect' },
        { title: 'Rendelés létrehozás előtt', value: 'beforeCollect' },
        { title: 'Rendelés folyamatban státusz után', value: 'afterOrder' },
        { title: 'Rendelés folyamatban státusz', value: 'beforeOrder' }
      ],
      urlRules: [
        v => !!v || 'URL megadása kötelező',
        v => {
          try {
            new URL(v);
            return true;
          } catch {
            return 'Érvényes URL-t adjon meg';
          }
        }
      ],
      timeRules: [
        v => !!v || 'Időpont megadása kötelező',
        v => /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/.test(v) || 'Érvényes időformátum: HH:MM'
      ],
      eventRules: [
        v => (v && v.length > 0) || 'Legalább egy eseményt válasszon ki'
      ]
    }
  },
  computed: {
    nextId() {
      return this.webhooks.length + 1
    }
  },
  mounted() {
    this.getWebhookList()
  },
  methods: {
    async getWebhookList() {
      try {
        this.isLoading = true;
        const response = await this.vendorStore.fetchWebhooks(this.vendorId);

        if (response.status === 200) {
          this.webhooks = response.data.data.vendors;
        }
      } catch (error) {
          console.error(error);
      } finally {
        this.isLoading = false;
      }
    },
    async addWebhook() {
      try {
        const response = await this.webhookStore.add({
          vendor_id: this.vendorId,
          url: '',
          message_template: '',
          trigger_type: 'event',
          scheduled_time: '',
          event_types: []
        })
        if (response.status === 201) {
          this.getWebhookList()
        }
      } catch (error) {
        console.error(error);
      }

    },
    async removeWebhook(id) {
      try {
        const response = await this.webhookStore.delete(id)
        if (response.status === 204) {
          this.getWebhookList()
        }
      } catch (error) {
        console.error(error);
      }
    },
    async saveWebhook(index) {
      const webhook = this.webhooks[index]

      // Get the form reference for this specific webhook
      const form = this.$refs.webhookForm[index]

      // Validate the form
      const { valid } = await form.validate()

      if (!valid) {
        console.log("Validációs hibák vannak")
        return false
      }

      try {
        const response = await this.webhookStore.update(webhook.id, webhook)
        if (response.status === 200) {
          this.getWebhookList()
          console.log("Webhook sikeresen mentve")
        }
      } catch (error) {
        console.error(error)
      }
    },
    async testWebhook(index) {
      const webhook = this.webhooks[index];

      // Get the form reference for this specific webhook
      const form = this.$refs.webhookForm[index]

      // Validate the form
      const { valid } = await form.validate()

      if (!valid) {
        console.log("Validációs hibák vannak, tesztelés meghiúsult")
        return false
      }

      try {
        const response = await this.webhookStore.test(webhook)
        if (response.status === 200) {
          this.getWebhookList()
          console.log("Webhook sikeresen mentve")
        }
      } catch (error) {
        console.error(error)
      }
    }
  }
}
</script>

<style scoped>
.bg-orange {
  background-color: #FF9800 !important;
}
</style>
