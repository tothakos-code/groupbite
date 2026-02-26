<template>
  <div v-if="auth.isLoggedIn">
    <!-- General Settings -->
    <v-card
      class="mb-4"
      elevation="2"
    >
      <v-card-title class="bg-primary text-white">
        <v-icon start>
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
              v-model="settings.app_title"
              label="Alkalmazás címe"
              prepend-icon="mdi-format-title"
              variant="outlined"
              density="comfortable"
            />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- SMTP Settings -->
    <v-card
      class="mb-4"
      elevation="2"
    >
      <v-card-title class="bg-secondary text-white">
        <v-icon start>
          mdi-email-outline
        </v-icon>
        Email küldés beállítások
      </v-card-title>
      <v-card-text class="pa-4">
        <v-row>
          <v-col
            cols="12"
            sm="6"
            md="4"
          >
            <v-text-field
              v-model="settings.smtp_address"
              label="SMTP szerver"
              prepend-icon="mdi-server"
              variant="outlined"
              density="comfortable"
              :error-messages="smtpAddressErrors"
              @blur="v$.settings.smtp_address.$touch()"
            />
          </v-col>
          <v-col
            cols="12"
            sm="6"
            md="4"
          >
            <v-text-field
              v-model="settings.smtp_port"
              label="SMTP port"
              prepend-icon="mdi-numeric"
              variant="outlined"
              density="comfortable"
              type="number"
              :error-messages="smtpPortErrors"
              @blur="v$.settings.smtp_port.$touch()"
            />
          </v-col>
        </v-row>

        <v-row>
          <v-col
            cols="12"
            sm="6"
            md="4"
          >
            <v-text-field
              v-model="settings.smtp_user"
              label="SMTP felhasználó"
              prepend-icon="mdi-account"
              variant="outlined"
              density="comfortable"
            />
          </v-col>
          <v-col
            cols="12"
            sm="6"
            md="4"
          >
            <v-text-field
              v-model="settings.smtp_password"
              label="SMTP jelszó"
              prepend-icon="mdi-lock"
              variant="outlined"
              density="comfortable"
              type="password"
            />
          </v-col>
        </v-row>

        <v-row>
          <v-col
            cols="12"
            md="8"
          >
            <v-alert
              type="warning"
              variant="tonal"
              density="compact"
            >
              Using SMTP servers with password authentication is not a good security practice.
              More secure methods are strongly recommended: SMTP relay, IP whitelisting, OAuth2,
              App-specific Password, or Certificate-Based Auth.
            </v-alert>
          </v-col>
        </v-row>

        <v-row>
          <v-col
            cols="12"
            sm="6"
            md="4"
          >
            <v-select
              v-model="settings.smtp_security"
              :items="smtpSecuritys"
              item-title="title"
              item-value="value"
              label="SMTP kapcsolat típusa"
              prepend-icon="mdi-shield-lock"
              variant="outlined"
              density="comfortable"
            />
          </v-col>
          <v-col
            cols="12"
            sm="6"
            md="4"
          >
            <v-text-field
              v-model="settings.smtp_sender_email"
              label="Email feladója"
              prepend-icon="mdi-email-arrow-right"
              variant="outlined"
              density="comfortable"
              :error-messages="smtpSenderErrors"
              @blur="v$.settings.smtp_sender_email.$touch()"
            />
          </v-col>
        </v-row>

        <v-divider class="my-4" />

        <!-- Test Email -->
        <v-row align="start">
          <v-col
            cols="12"
            sm="6"
            md="4"
          >
            <v-text-field
              v-model="testEmail"
              label="Teszt email cím"
              prepend-icon="mdi-email-check"
              variant="outlined"
              density="comfortable"
              :error-messages="testEmailErrors"
              @blur="v$.testEmail.$touch()"
            />
          </v-col>
          <v-col
            cols="12"
            sm="auto"
            class="d-flex align-center"
          >
            <v-btn
              color="secondary"
              prepend-icon="mdi-send"
              :disabled="v$.testEmail.$invalid || v$.settings.$invalid"
              @click="sendTestEmail"
            >
              Teszt email küldése
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Error state -->
    <v-alert
      v-if="isError"
      type="error"
      variant="tonal"
      class="mb-4"
    >
      Hiba történt a kérés során.
    </v-alert>

    <!-- Loading state -->
    <v-row
      v-if="isLoading"
      justify="center"
      class="my-8"
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
        <p class="mt-4">
          Beállítások betöltése...
        </p>
      </v-col>
    </v-row>

    <!-- Actions -->
    <v-card
      v-if="!isLoading"
      elevation="2"
    >
      <v-card-actions class="pa-4">
        <v-btn
          color="primary"
          size="large"
          prepend-icon="mdi-content-save"
          @click="saveSettings"
        >
          Mentés
        </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
import axios from 'axios'
import { useAuth } from '@/stores/auth'
import { notify } from '@kyvg/vue3-notification'
import useVuelidate from '@vuelidate/core'
import { required, email } from '@vuelidate/validators'

export default {
  name: 'AdminSettingsView',
  setup() {
    const auth = useAuth()
    return { auth, v$: useVuelidate() }
  },
  data() {
    return {
      settings: {
        smtp_address: '',
        smtp_port: '',
        smtp_sender_email: '',
        smtp_security: 'plain',
      },
      smtpSecuritys: [
        { title: 'Plain', value: 'plain' },
        { title: 'SSL',   value: 'ssl'   },
        { title: 'TLS',   value: 'tls'   },
      ],
      testEmail: '',
      isLoading: true,
      isError: false,
    }
  },
  validations() {
    return {
      testEmail: { required, email },
      settings: {
        smtp_address:      { required },
        smtp_port:         { required },
        smtp_sender_email: { required, email },
      },
    }
  },
  computed: {
    smtpAddressErrors() {
      if (!this.v$.settings.smtp_address.$dirty) return []
      return this.v$.settings.smtp_address.$invalid ? ['SMTP szerver nem lehet üres!'] : []
    },
    smtpPortErrors() {
      if (!this.v$.settings.smtp_port.$dirty) return []
      return this.v$.settings.smtp_port.$invalid ? ['SMTP port nem lehet üres!'] : []
    },
    smtpSenderErrors() {
      if (!this.v$.settings.smtp_sender_email.$dirty) return []
      return this.v$.settings.smtp_sender_email.$invalid ? ['Email feladója érvénytelen vagy üres!'] : []
    },
    testEmailErrors() {
      if (!this.v$.testEmail.$dirty) return []
      return this.v$.testEmail.$invalid ? ['Teszt fogadó email nem lehet üres vagy érvénytelen!'] : []
    },
  },
  mounted() {
    this.getSettings()
  },
  methods: {
    getSettings() {
      axios.get(`http://${window.location.host}/api/setting/get-all`)
        .then((response) => {
          this.settings = response.data
          this.isLoading = false
        })
        .catch((e) => {
          console.error(e)
          this.isError = true
          notify({ type: 'error', text: 'Hiba történt a kérés során.' })
        })
    },

    saveSettings() {
      this.v$.$reset()
      if (this.settings.smtp_address) {
        this.v$.settings.smtp_address.$touch()
        this.v$.settings.smtp_port.$touch()
        this.v$.settings.smtp_sender_email.$touch()
      }
      if (
        this.settings.smtp_address && (
          this.v$.settings.smtp_address.$invalid ||
          this.v$.settings.smtp_port.$invalid ||
          this.v$.settings.smtp_sender_email.$invalid
        )
      ) return

      axios.put(`http://${window.location.host}/api/setting/set`, this.settings)
        .then(() => notify({ type: 'info', text: 'Beállítások mentése sikerült!' }))
        .catch((e) => {
          console.error(e)
          notify({ type: 'error', text: 'Beállítások mentése nem sikerült!' })
        })
    },

    sendTestEmail() {
      this.v$.$touch()
      if (this.v$.$invalid) return

      axios.post(`http://${window.location.host}/api/setting/mail/send-test`, {
        'test-email':       this.testEmail,
        smtp_address:       this.settings.smtp_address,
        smtp_port:          this.settings.smtp_port,
        smtp_user:          this.settings.smtp_user,
        smtp_password:      this.settings.smtp_password,
        smtp_sender_email:  this.settings.smtp_sender_email,
        smtp_security:      this.settings.smtp_security,
      })
        .then(() => notify({ type: 'info', text: 'Teszt email elküldve.' }))
        .catch((e) => {
          console.error(e)
          notify({ type: 'error', text: 'Hiba történt a kérés során.: ' + e.response.data.error })
        })
    },
  },
}
</script>
