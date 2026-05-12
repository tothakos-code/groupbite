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
              >{{ vendor.name }}</span>
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
              <template
                v-for="section in sections"
                :key="section.id"
              >
                <v-divider
                  v-if="section.divider"
                  class="my-2"
                />
                <v-tooltip
                  v-else
                  :text="section.label"
                  :disabled="!navCollapsed"
                  location="right"
                >
                  <template #activator="{ props }">
                    <v-list-item
                      v-bind="props"
                      :value="section.id"
                      :active="!section.navigate && activeSection === section.id"
                      :color="section.color"
                      rounded="lg"
                      class="nav-item"
                      @click="handleNavClick(section)"
                    >
                      <template #prepend>
                        <v-icon :color="!section.navigate && activeSection === section.id ? section.color : ''">
                          {{ section.icon }}
                        </v-icon>
                      </template>
                      <v-list-item-title
                        v-if="!navCollapsed"
                        class="nav-item-title"
                      >
                        {{ section.label }}
                      </v-list-item-title>
                    </v-list-item>
                  </template>
                </v-tooltip>
              </template>
            </v-list>

            <!-- Save / Reset pinned to bottom -->
            <div class="nav-footer">
              <v-divider class="mb-3" />
              <v-tooltip
                text="Mentés"
                :disabled="!navCollapsed"
                location="right"
              >
                <template #activator="{ props }">
                  <v-btn
                    v-bind="props"
                    color="primary"
                    :icon="navCollapsed"
                    :loading="saving"
                    :block="!navCollapsed"
                    size="small"
                    class="mb-2"
                    @click="saveSettings"
                  >
                    <v-icon :start="!navCollapsed">
                      mdi-content-save
                    </v-icon>
                    <span v-if="!navCollapsed">Mentés</span>
                  </v-btn>
                </template>
              </v-tooltip>

              <v-tooltip
                text="Visszaállítás"
                :disabled="!navCollapsed"
                location="right"
              >
                <template #activator="{ props }">
                  <v-btn
                    v-bind="props"
                    color="primary"
                    variant="outlined"
                    :icon="navCollapsed"
                    :block="!navCollapsed"
                    size="small"
                    @click="resetForm"
                  >
                    <v-icon :start="!navCollapsed">
                      mdi-refresh
                    </v-icon>
                    <span v-if="!navCollapsed">Visszaállítás</span>
                  </v-btn>
                </template>
              </v-tooltip>
            </div>
          </nav>

          <!-- Main Content — only the active section is rendered -->
          <main class="settings-content">
            <transition
              name="fade"
              mode="out-in"
            >
              <div :key="activeSection">
                <VendorMenuManager
                  v-if="activeSection === 'menu' && !selectedMenuId"
                  :key="'menu-' + $route.params.id"
                  @select-menu="selectedMenuId = $event"
                />
                <VendorItemManager
                  v-else-if="activeSection === 'menu' && selectedMenuId"
                  :key="'items-' + selectedMenuId"
                  :inline-menu-id="selectedMenuId"
                  @back="selectedMenuId = null"
                />
                <VendorOptionGroupManager
                  v-else-if="activeSection === 'option-groups'"
                  :key="'og-' + $route.params.id"
                />
                <VendorBundleManager
                  v-else-if="activeSection === 'bundles'"
                  :key="'b-' + $route.params.id"
                />
                <CategoryManager
                  v-else-if="activeSection === 'categories'"
                  :vendor-id="$route.params.id"
                />
                <GeneralSettings
                  v-else-if="activeSection === 'general'"
                  v-model:settings="vendor.settings"
                />
                <UiSettings
                  v-else-if="activeSection === 'ui'"
                  v-model:settings="vendor.settings"
                />
                <OrderTimingSettings
                  v-else-if="activeSection === 'timing'"
                  v-model:settings="vendor.settings"
                  :smtp-status="smtpStatus"
                />
                <AutoEmailSettings
                  v-else-if="activeSection === 'email'"
                  v-model:settings="vendor.settings"
                />
                <WebhookSettings
                  v-else-if="activeSection === 'webhook'"
                  :vendor-id="vendor.id"
                />
                <PluginSettings
                  v-else-if="activeSection === 'plugin'"
                  v-model:settings="pluginSettings"
                  :plugin-id="vendor.plugin_id"
                />
              </div>
            </transition>
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
import { useRouter } from 'vue-router'
import { notify } from '@kyvg/vue3-notification'
import axios from 'axios'
import WebhookSettings from '@/components/vendor-settings/WebhookSettings.vue'
import GeneralSettings from '@/components/vendor-settings/GeneralSettings.vue'
import UiSettings from '@/components/vendor-settings/UiSettings.vue'
import OrderTimingSettings from '@/components/vendor-settings/OrderTimingSettings.vue'
import AutoEmailSettings from '@/components/vendor-settings/AutoEmailSettings.vue'
import PluginSettings from '@/components/vendor-settings/PluginSettings.vue'
import CategoryManager from '@/components/item-manager/CategoryManager.vue'
import VendorMenuManager from '@/views/admin/vendor/VendorMenuManager.vue'
import VendorItemManager from '@/views/admin/vendor/VendorItemManager.vue'
import VendorOptionGroupManager from '@/views/admin/vendor/VendorOptionGroupManager.vue'
import VendorBundleManager from '@/views/admin/vendor/VendorBundleManager.vue'

export default {
  name: 'VendorSettings',
  components: {
    WebhookSettings,
    GeneralSettings,
    UiSettings,
    OrderTimingSettings,
    AutoEmailSettings,
    PluginSettings,
    CategoryManager,
    VendorMenuManager,
    VendorItemManager,
    VendorOptionGroupManager,
    VendorBundleManager,
  },
  setup() {
    const auth = useAuth()
    const vendorStore = useVendorStore()
    const router = useRouter()
    const form = ref()
    return { auth, vendorStore, router, form }
  },
  data() {
    return {
      vendor: {},
      originalVendor: {},
      pluginSettings: {},
      isLoading: true,
      saving: false,
      smtpStatus: false,
      navCollapsed: false,
      activeSection: this.$route.params.section || 'general',
      selectedMenuId: null,
      sections: [
        { id: 'menu',          label: 'Menükezelés',          icon: 'mdi-food',         color: 'primary' },
        { id: 'option-groups', label: 'Opció csoportok',      icon: 'mdi-tune',         color: 'primary' },
        { id: 'bundles',       label: 'Menü ajánlatok',       icon: 'mdi-tag-multiple', color: 'primary' },
        { id: 'categories',    label: 'Kategóriakezelés',     icon: 'mdi-tag-multiple', color: 'primary' },
        { id: '_divider', divider: true },
        { id: 'general',    label: 'Általános',            icon: 'mdi-cog',           color: 'primary' },
        { id: 'ui',         label: 'Felhasználói felület', icon: 'mdi-palette',       color: 'primary' },
        { id: 'timing',     label: 'Időzítés',             icon: 'mdi-clock-outline', color: 'primary' },
        { id: 'email',      label: 'Automatikus email',    icon: 'mdi-email-fast',    color: 'primary' },
        { id: 'webhook',    label: 'Webhook',              icon: 'mdi-webhook',       color: 'primary' },
      ],
    }
  },
  watch: {
    '$route.params.section'(section) {
      if (section) this.activeSection = section
    },
  },
  mounted() {
    this.getSettings()
  },
  methods: {
    handleNavClick(section) {
      this.activeSection = section.id
      if (section.id === 'menu') this.selectedMenuId = null
      this.$router.push({ params: { section: section.id } })
    },

    async getSettings() {
      try {
        this.isLoading = true
        const response = await this.vendorStore.fetchVendorSettings(this.$route.params.id)
        this.vendor = response.data.data
        this.initializeNewSettings()
        this.originalVendor = JSON.parse(JSON.stringify(this.vendor))
        await this.checkSmtpStatus()
        if (this.vendor.plugin_id) {
          await this.loadPluginSettings()
          this.sections.push({ id: 'plugin', label: this.$t('vendor.plugin.settings'), icon: 'mdi-puzzle', color: 'primary' })
        }
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
        show_favourites:             { name: 'Kedvencek megjelenítése',                    value: true  },
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

    async loadPluginSettings() {
      const response = await this.vendorStore.fetchPluginSettings(this.$route.params.id)
      if (response?.status === 200) {
        this.pluginSettings = response.data.data.settings
      }
    },

    async saveSettings() {
      try {
        const { valid } = await this.$refs.form.validate()
        if (!valid) {
          notify({ type: 'warn', text: 'Kérjük javítsa ki a hibákat a mentés előtt.' })
          return
        }
        this.saving = true
        if (this.activeSection === 'plugin') {
          const values = Object.fromEntries(
            Object.entries(this.pluginSettings).map(([k, s]) => [k, s.value])
          )
          await this.vendorStore.savePluginSettings(this.$route.params.id, values)
          await this.loadPluginSettings()
        } else {
          await this.vendorStore.saveSettings(this.$route.params.id, this.vendor.settings)
          this.$toast?.success('Beállítások sikeresen mentve')
          this.originalVendor = JSON.parse(JSON.stringify(this.vendor))
        }
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
  height: calc(100vh - 64px); /* adjust to your app toolbar height */
  overflow: hidden;
}

/* ── Sidebar ─────────────────────────────────────────── */
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

.nav-list {
  flex: 1;
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

.nav-footer {
  padding: 8px 10px 16px;
}

/* ── Content panel ───────────────────────────────────── */
.settings-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}

/* ── Fade transition between panels ─────────────────── */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.fade-enter-from {
  opacity: 0;
  transform: translateX(8px);
}
.fade-leave-to {
  opacity: 0;
  transform: translateX(-8px);
}

/* ── Mobile ──────────────────────────────────────────── */
@media (max-width: 768px) {
  .settings-nav {
    width: 64px;
    min-width: 64px;
  }
}
</style>
