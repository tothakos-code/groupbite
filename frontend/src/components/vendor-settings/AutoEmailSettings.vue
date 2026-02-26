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
        <div v-if="settings.auto_email_order.value">
          <v-divider class="my-4" />

          <v-row>
            <v-col
              cols="12"
              md="6"
            >
              <v-combobox
                v-model="settings.auto_email_order_to.value"
                chips
                multiple
                :label="settings.auto_email_order_to.name"
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
                v-model="settings.auto_email_order_cc.value"
                chips
                multiple
                :label="settings.auto_email_order_cc.name"
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
                v-model="settings.auto_email_subject.value"
                :label="settings.auto_email_subject.name"
                prepend-icon="mdi-format-title"
                variant="outlined"
                density="comfortable"
              />
            </v-col>
          </v-row>

          <v-row>
            <v-col cols="12">
              <v-textarea
                v-model="settings.auto_email_order_template.value"
                :label="settings.auto_email_order_template.name"
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
</template>

<script>
export default {
  name: 'AutoEmailSettings',
  props: {
    settings: {
      type: Object,
      required: true,
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
</style>
