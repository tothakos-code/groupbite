<template>
  <div class="row ms-2 mt-2">
    <h1 class="col d-flex justify-content-start">
      Alkalmazás beállítások
    </h1>
  </div>
  <div class="row ms-2 mt-2">
    <div
      v-if="!isLoading"
      class=""
    >
      <h5 class="text-secondary">
        Álltalános beállítások
      </h5>
      <hr class="mt-1">
      <div class="row">
        <div class="col-auto">
          <label for="name">
            Alkalmazás címe
          </label>
          <input
            v-model="settings.app_title"
            class="form-control"
            type="text"
            name="name"
          >
        </div>
      </div>
      <h5 class="text-secondary mt-5">
        Email küldés beállítások
      </h5>
      <hr class="mt-1">
      <form
        class="needs-validation"
        @submit.prevent="validateSMTPSettings()"
      >
        <div class="">
          <div class="row mb-2">
            <div class="col-auto">
              <label
                class="form-label"
                for="smtp_address"
              >
                SMTP szerver:
              </label>
              <input
                id="smtp_address"
                v-model="settings.smtp_address"
                class="form-control"
                :class="{'is-invalid': v$.settings.smtp_address.$invalid && v$.settings.smtp_address.$dirty}"
                type="text"
                name="smtp_address"
              >
              <div class="invalid-feedback">
                SMTP szerver nem lehet üres!
              </div>
            </div>
            <div class="col-auto">
              <label
                class="form-label"
                for="smtp_port"
              >
                SMTP port:
              </label>
              <input
                id="smtp_port"
                v-model="settings.smtp_port"
                class="form-control"
                :class="v$.settings.smtp_port.$error?'is-invalid':''"
                type="number"
                name="smtp_port"
              >
              <div class="invalid-feedback">
                SMTP port nem lehet üres!
              </div>
            </div>
          </div>
          <div class="row">
            <div class="row mb-2">
              <div class="col-auto">
                <label
                  class="form-label"
                  for="smtp_user"
                >
                  SMTP felhasználó:
                </label>
                <input
                  id="smtp_user"
                  v-model="settings.smtp_user"
                  class="form-control"
                  type="text"
                  name="smtp_user"
                >
              </div>
              <div class="col-auto">
                <div class="">
                  <label
                    class="form-label"
                    for="smtp_password"
                  >
                    SMTP jelszó:
                  </label>
                  <input
                    id="smtp_password"
                    v-model="settings.smtp_password"
                    class="form-control"
                    type="password"
                    name="smtp_password"
                    aria-describedby="smtp-password-warning"
                  >
                </div>
              </div>
              <div
                id="smtp-password-warning"
                class="form-text text-break text-wrap col-6"
              >
                Warning! Using SMPT servers with a password authentication is not a good security practice! The SMTP password you enter here will be stored in plain text to allow the server to authenticate with your SMTP server. Alternative more secure auth methods adviced: IP whitelisting, OAuth2, App-specific Password, Certificate-Based Auth. Use at your own risk in production!
              </div>
            </div>
            <div class="row mb-2">
              <div class="col-auto">
                <label
                  class="form-label"
                  for="smtp_sender_email"
                >
                  Email feladója:
                </label>
                <input
                  id="smtp_sender_email"
                  v-model="settings.smtp_sender_email"
                  :class="{'is-invalid': v$.settings.smtp_sender_email.$invalid && v$.settings.smtp_sender_email.$dirty}"
                  class="form-control"
                  type="text"
                  name="smtp_sender_email"
                >
                <div
                  v-if="v$.settings.smtp_sender_email.$invalid && v$.settings.smtp_sender_email.$dirty"
                  class="invalid-feedback"
                >
                  Email feladója nem lehet üres
                </div>
              </div>
            </div>
            <div class="row mb-2">
              <div class="col-auto">
                <label
                  class="form-label"
                  for="test_email"
                >
                  Teszt Email cím:
                </label>
                <input
                  id="test_email"
                  v-model="testEmail"
                  :class="{'is-invalid': v$.testEmail.$invalid && v$.testEmail.$dirty}"
                  class="form-control"
                  type="text"
                  name="test_email"
                >
                <div
                  v-if="v$.testEmail.$invalid && v$.testEmail.$dirty"
                  class="invalid-feedback"
                >
                  Teszt fogadó email nem lehet üres
                </div>
              </div>
              <div
                class="col-auto d-flex align-items-end"
                :class="{'align-items-center mt-1': v$.testEmail.$invalid && v$.testEmail.$dirty}"
              >
                <div class="">
                  <v-btn
                    type="submit"
                    name="button"
                    varian="text"
                    class="text-primary bg-background"
                    border="primary thin"
                    @click="sendTestEmail()"
                  >
                    Teszt Email küldése
                  </v-btn>
                </div>
              </div>
            </div>
          </div>
        </div>
      </form>
      <hr>
      <div class="mt-3">
        <v-btn
          type="submit"
          name="button"
          varian="text"
          class="text-primary bg-background"
          border="primary thin"
          @click="saveSettings()"
        >
          Mentés
        </v-btn>
      </div>
    </div>
    <div v-if="isError">
      <p>Hiba történt a kérés során.</p>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { useAuth } from "@/stores/auth";
import { notify } from "@kyvg/vue3-notification";
import useVuelidate from '@vuelidate/core'
import { required, email} from '@vuelidate/validators'

export default {
    name: "AdminSettingsView",
    setup() {
      const auth = useAuth();
      return {
        auth,
        v$: useVuelidate()
      }
    },
    data() {
      return {
        settings: {
          smtp_address: "",
          smtp_port: "",
          smtp_sender_email: "",
        },
        testEmail: "",
        isLoading: true,
        isError: false,
      }
    },
    validations() {
      return {
        testEmail: { required, email },
        settings: {
          smtp_address: { required },
          smtp_port: { required },
          smtp_sender_email: { required, email },
        },
      }
    },
    mounted() {
      this.getSettings()
    },
    methods: {
      openAdminHome: function () {
        this.$router.push({ path:`/admin/settings`})
      },
      getSettings: function () {
        axios.get(`http://${window.location.host}/api/setting/get-all`)
          .then(response => {
            this.settings = response.data;
            // this.v$ = useVuelidate(this.rules, this.settings);
            this.isLoading = false;
          })
          .catch(e => {
              console.log(e);
              this.isError = true;
              notify({
                type: "error",
                text: "Hiba történt a kérés során.",
              });
          })
      },
      saveSettings: function () {
        this.v$.$reset()
        if (this.settings.smtp_address) {
          this.v$.settings.smtp_address.$touch();
          this.v$.settings.smtp_port.$touch();
          this.v$.settings.smtp_sender_email.$touch();

        }
        if (
          this.v$.settings.smtp_address.$invalid ||
          this.v$.settings.smtp_port.$invalid ||
          this.v$.settings.smtp_sender_email.$invalid
          ) {
          console.log(this.v$);
          return
        }
        axios.put(`http://${window.location.host}/api/setting/set`, this.settings)
          .then(() => {
            notify({
              type: "info",
              text: "Beállítások mentése sikerült!",
            });
          })
          .catch(e => {
            console.log(e);
            notify({
              type: "error",
              text: "Beállítások mentése nem sikerült!",
            });
          })
      },
      sendTestEmail: function () {
        if (this.v$.$invalid) {
          return
        }
        axios.post(`http://${window.location.host}/api/setting/mail/send-test`,
          {
            "test-email": this.testEmail,
            "smtp_address": this.settings.smtp_address,
            "smtp_port": this.settings.smtp_port,
            "smtp_user": this.settings.smtp_user,
            "smtp_password": this.settings.smtp_password,
            "smtp_sender_email": this.settings.smtp_sender_email
          })
          .then(() => {
            notify({
              type: "info",
              text: "Teszt email elküldve.",
            });
          })
          .catch(e => {
              console.log(e);
              notify({
                type: "error",
                text: "Hiba történt a kérés során.: "  + e.response.data.error,
              });
          })
      },
      validateSMTPSettings: function () {
        this.v$.$touch();
      }

    }

};
</script>

<style scoped>
</style>
