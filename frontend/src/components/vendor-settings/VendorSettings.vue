<template>
  <div class="vendor-settings-layout">
    <!-- Loading State -->
    <v-container v-if="isLoading">
      <v-row
        justify="center"
        class="mt-8"
      >
        <v-col
          cols="auto"
          class="text-center"
        >
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

    <template v-else>
      <v-form ref="form">
        <div class="settings-container">
          <!-- Left Navigation Rail -->
          <nav
            class="settings-nav"
            :class="{ 'settings-nav--collapsed': navCollapsed }"
          >
            <div class="nav-header">
              <span
                v-if="!navCollapsed"
                class="nav-title"
              >Beállítások</span>
              <v-btn
                :icon="navCollapsed ? 'mdi-chevron-right' : 'mdi-chevron-left'"
                variant="text"
                size="small"
                class="collapse-btn"
                @click="navCollapsed = !navCollapsed"
              />
            </div>

            <v-list
              density="compact"
              nav
              class="nav-list"
            >
              <v-list-item
                v-for="section in sections"
                :key="section.id"
                :value="section.id"
                :active="activeSection === section.id"
                :active-color="section.color"
                rounded="lg"
                class="nav-item"
                @click="scrollToSection(section.id)"
              >
                <template #prepend>
                  <v-icon :color="activeSection === section.id ? section.color : ''">
                    {{ section.icon }}
                  </v-icon>
                </template>
                <v-list-item-title
                  v-if="!navCollapsed"
                  class="nav-item-title"
                >
                  {{ section.label }}
                </v-list-item-title>

                <template
                  v-if="navCollapsed && activeSection === section.id"
                  #append
                >
                  <span
                    class="active-dot"
                    :style="{ background: `rgb(var(--v-theme-${section.color}))` }"
                  />
                </template>
              </v-list-item>
            </v-list>

            <!-- Save button pinned to bottom of nav -->
            <div class="nav-footer">
              <v-divider class="mb-3" />
              <v-tooltip
                :text="navCollapsed ? 'Mentés' : ''"
                location="right"
              >
                <template #activator="{ props }">
                  <v-btn
                    v-bind="props"
                    color="primary"
                    :icon="navCollapsed ? 'mdi-content-save' : undefined"
                    :prepend-icon="navCollapsed ? undefined : 'mdi-content-save'"
                    :loading="saving"
                    :block="!navCollapsed"
                    size="small"
                    @click="saveSettings"
                  >
                    <span v-if="!navCollapsed">Mentés</span>
                  </v-btn>
                </template>
              </v-tooltip>
            </div>
          </nav>

          <!-- Main Content -->
          <main
            ref="contentRef"
            class="settings-content"
            @scroll="onContentScroll"
          >
            <section
              id="section-general"
              class="settings-section"
            >
              <GeneralSettings :settings="vendor.settings" />
            </section>

            <section
              id="section-ui"
              class="settings-section"
            >
              <UiSettings :settings="vendor.settings" />
            </section>

            <section
              id="section-timing"
              class="settings-section"
            >
              <OrderTimingSettings
                :settings="vendor.settings"
                :smtp-status="smtpStatus"
              />
            </section>

            <section
              id="section-email"
              class="settings-section"
            >
              <AutoEmailSettings :settings="vendor.settings" />
            </section>

            <section
              id="section-webhook"
              class="settings-section"
            >
              <WebhookSettings :vendor-id="vendor.id" />
            </section>

            <!-- Bottom Action Bar -->
            <v-card
              elevation="2"
              class="mb-4"
            >
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
          </main>
        </div>
      </v-form>
    </template>
  </div>
</template>

<script>
import { useVendorStore } from '@/stores/vendor'
import { useAuth } from '@/stores/auth'
import { ref } from 'vue'
import axios from 'axios'
import WebhookSettings from '@/components/vendor/WebhookSettings.vue'
import GeneralSettings from '@/components/vendor-settings/GeneralSettings.vue'
import UiSettings from '@/components/vendor-settings/UiSettings.vue'
import OrderTimingSettings from '@/components/vendor-settings/OrderTimingSettings.vue'
import AutoEmailSettings from '@/components/vendor-settings/AutoEmailSettings.vue'

export default {
  name: 'VendorSettings',
  components: {
    WebhookSettings,
    GeneralSettings,
    UiSettings,
    OrderTimingSettings,
    AutoEmailSettings,
  },
  setup() {
    const auth = useAuth()
    const vendorStore = useVendorStore()
    const form = ref()
    const contentRef = ref()
    return { auth, vendorStore, form, contentRef }
  },
  data() {
    return {
      vendor: {},
      originalVendor: {},
      isLoading: true,
      saving: false,
      smtpStatus: false,
      navCollapsed: false,
      activeSection: 'general',
      sections: [
        { id: 'general', label: 'Általános',             icon: 'mdi-cog',           color: 'primary'   },
        { id: 'ui',      label: 'Felhasználói felület',  icon: 'mdi-palette',        color: 'secondary' },
        { id: 'timing',  label: 'Időzítés',              icon: 'mdi-clock-outline',  color: 'warning'   },
        { id: 'email',   label: 'Automatikus email',     icon: 'mdi-email-fast',     color: 'success'   },
        { id: 'webhook', label: 'Webhook',               icon: 'mdi-webhook',        color: 'info'      },
      ],
    }
  },
  mounted() {
    this.getSettings()
  },
  methods: {
    async getSettings() {
      try {
        this.isLoading = true
        const response = await this.vendorStore.fetchVendor(this.$route.params.id)
        this.vendor = response.data.data
        this.initializeNewSettings()
        this.originalVendor = JSON.parse(JSON.stringify(this.vendor))
        await this.checkSmtpStatus()
      } catch (error) {
        console.error('Error loading settings:', error)
        this.$toast?.error('Hiba a beállítások betöltése során')
      } finally {
        this.isLoading = false
      }
    },

    initializeNewSettings() {
      const defaults = {
        enable_full_automatic_order: { name: 'Teljes automatikus rendelés engedélyezése', value: false },
        enable_email_order:          { name: 'Email rendelés engedélyezése',               value: false },
        enable_manual_order:         { name: 'Manuális rendelés engedélyezése',            value: true  },
        show_notification_button:    { name: 'Értesítési gomb megjelenítése',              value: true  },
      }
      Object.keys(defaults).forEach((key) => {
        if (!this.vendor.settings[key]) this.vendor.settings[key] = defaults[key]
      })
    },

    async checkSmtpStatus() {
      try {
        const response = await axios.get('/api/setting/get/smtp_address')
        this.smtpStatus = response.status === 200 && response.data.smtp_address !== ''
      } catch {
        this.smtpStatus = false
      }
    },

    scrollToSection(id) {
      this.activeSection = id
      const container = this.$refs.contentRef
      const el = container?.querySelector(`#section-${id}`)
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    },

    onContentScroll() {
      const container = this.$refs.contentRef
      if (!container) return
      // Walk sections in reverse; highlight the last one whose top is within view
      for (const section of [...this.sections].reverse()) {
        const el = container.querySelector(`#section-${section.id}`)
        if (!el) continue
        if (el.offsetTop - container.scrollTop <= 80) {
          this.activeSection = section.id
          break
        }
      }
    },

    async saveSettings() {
      try {
        const { valid } = await this.$refs.form.validate()
        if (!valid) {
          this.$toast?.error('Kérjük javítsa ki a hibákat a mentés előtt')
          return
        }
        this.saving = true
        await this.vendorStore.saveSettings(this.$route.params.id, this.vendor.settings)
        this.$toast?.success('Beállítások sikeresen mentve')
        this.originalVendor = JSON.parse(JSON.stringify(this.vendor))
      } catch (error) {
        console.error('Error saving settings:', error)
        this.$toast?.error('Hiba a beállítások mentése során')
      } finally {
        this.saving = false
      }
    },

    resetForm() {
      this.vendor = JSON.parse(JSON.stringify(this.originalVendor))
      this.$refs.form.resetValidation()
    },
  },
}
</script>

<style scoped>
.vendor-settings-layout {
  height: 100%;
}

.settings-container {
  display: flex;
  /* Subtract your app's top bar height — adjust 64px as needed */
  height: calc(100vh - 64px);
  overflow: hidden;
}

/* ── Sidebar navigation ──────────────────────────────── */
.settings-nav {
  display: flex;
  flex-direction: column;
  width: 220px;
  min-width: 220px;
  background: rgb(var(--v-theme-surface));
  border-right: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  transition: width 0.25s ease, min-width 0.25s ease;
  overflow: hidden;
}

.settings-nav--collapsed {
  width: 64px;
  min-width: 64px;
}

.nav-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 10px 6px;
  min-height: 52px;
}

.nav-title {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(var(--v-theme-on-surface), 0.45);
  white-space: nowrap;
}

.collapse-btn {
  flex-shrink: 0;
}

.nav-list {
  flex: 1;
  overflow-y: auto;
  padding: 4px 8px;
}

.nav-item {
  margin-bottom: 2px;
}

.nav-item-title {
  font-size: 0.85rem;
  font-weight: 500;
  white-space: nowrap;
}

.active-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: block;
  margin-left: 4px;
}

.nav-footer {
  padding: 8px 10px 16px;
}

/* ── Main scrollable content ─────────────────────────── */
.settings-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}

.settings-section {
  scroll-margin-top: 16px;
}

/* ── Mobile: auto-collapse sidebar ──────────────────── */
@media (max-width: 768px) {
  .settings-nav {
    width: 64px;
    min-width: 64px;
  }
}
</style>
