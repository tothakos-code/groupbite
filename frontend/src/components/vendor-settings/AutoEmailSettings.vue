<template>
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
        <div v-if="localSettings.auto_email_order">
          <v-divider class="my-4" />

          <v-row>
            <v-col
              cols="12"
              md="6"
            >
              <v-combobox
                v-model="localSettings.auto_email_order_to"
                chips
                multiple
                :label="$t('vendor.settings.auto_email_order_to')"
                :rules="[(v) => validateEmails(v, true)]"
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
                v-model="localSettings.auto_email_order_cc"
                chips
                multiple
                :label="$t('vendor.settings.auto_email_order_cc')"
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
                v-model="localSettings.auto_email_subject"
                :label="$t('vendor.settings.auto_email_subject')"
                prepend-icon="mdi-format-title"
                variant="outlined"
                density="comfortable"
              />
            </v-col>
          </v-row>

          <v-row>
            <v-col cols="12">
              <v-textarea
                :model-value="isDefault ? DEFAULT_TEMPLATE : localSettings.auto_email_order_template"
                :label="$t('vendor.settings.auto_email_order_template')"
                :hint="isDefault ? $t('vendor.settings.auto_email_template_hint_default') : $t('vendor.settings.auto_email_template_hint_edited')"
                :persistent-hint="true"
                :class="['code-textarea', { 'template-default': isDefault }]"
                prepend-icon="mdi-file-document-edit"
                variant="outlined"
                rows="4"
                auto-grow
                @update:model-value="val => { localSettings.auto_email_order_template = val }"
              />
            </v-col>
          </v-row>

          <v-row v-if="!isDefault">
            <v-col cols="12">
              <v-btn
                variant="plain"
                size="small"
                prepend-icon="mdi-restore"
                @click="localSettings.auto_email_order_template = ''"
              >
                {{ $t('vendor.settings.auto_email_template_reset') }}
              </v-btn>
            </v-col>
          </v-row>
        </div>
      </v-expand-transition>
    </v-card-text>
  </v-card>
</template>

<script>
const DEFAULT_TEMPLATE = `{% for category, items in categories.items() %}
{{ category }}:
{% for item in items %}
  - {{ item.item_name }}{% if item.size_name %} ({{ item.size_name }}){% endif %} x{{ item.quantity }}
{% for option in item.options %}    + {{ option.choice }}{% if option.group %} ({{ option.group }}){% endif %}
{% endfor %}{% endfor %}
{% endfor %}
{% if order_note %}Megjegyzés: {{ order_note }}
{% endif %}`

export default {
  name: 'AutoEmailSettings',
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
      DEFAULT_TEMPLATE,
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
  computed: {
    isDefault() {
      return !this.localSettings.auto_email_order_template
    },
  },
  methods: {
    validateEmails(value, required = false) {
      if (required && (!value || value.length === 0)) {
        return 'Legalább egy email cím szükséges.'
      }
      if (!value || value.length === 0) return true

      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      const invalidEmails = value.filter((email) => !emailPattern.test(email))

      if (invalidEmails.length > 0) {
        return `Érvénytelen email címek: ${invalidEmails.join(', ')}`
      }
      return true
    },
  },
}
</script>

<style scoped>
.code-textarea {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 13px;
  line-height: 1.5;
}

.template-default :deep(textarea) {
  color: rgba(var(--v-theme-on-surface), 0.38);
}
</style>
