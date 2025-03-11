<template>
  <div class="row ms-2">
    <v-container
      v-if="!isLoading"
      class=""
    >
      <v-form ref="form">
        <h5 class="mt-2">
          Álltalános beállítások
        </h5>
        <hr class="mt-1">
        <v-text-field
          v-model="vendor.settings.title.value"
          :label="vendor.settings.title.name"
          required
          bg-color="white"
        />
        <v-text-field
          v-model="vendor.settings.link.value"
          :label="vendor.settings.link.name"
          bg-color="white"
        />
        <v-text-field
          v-model="vendor.settings.comment_example.value"
          :label="vendor.settings.comment_example.name"
          bg-color="white"
        />
        <v-text-field
          v-model.number="vendor.settings.transport_price.value"
          :label="vendor.settings.transport_price.name"
          :rules="[
            v => !!v || v===0 || 'Kötelező mező',
            v => /^\d+$/.test(v) || 'Csak szám lehetséges'
          ]"
          type="number"
          bg-color="white"
          hint="Rendelés díj (szállítási díj, rendszerhasználat díj, egyebek felszámolása) Az összeg szétlessz osztva a rendelésben résztvevők között arányosan"
        />
        <h5 class="mt-2">
          Rendelés folyamat beállítások
        </h5>
        <hr class="mt-1">
        <v-row class="">
          <v-checkbox
            v-model="vendor.settings.closed_scheduler_active.value"
            color="primary"
            :label="vendor.settings.closed_scheduler_active.name"
            class="ms-2"
          />
          <v-text-field
            v-model="vendor.settings.closed_scheduler.value"
            :label="vendor.settings.closed_scheduler.name"
            :disabled="!vendor.settings.closed_scheduler_active.value"
            :rules="[
              v => !vendor.settings.closed_scheduler_active.value || !!v || 'Kötelező mező',
              v => !vendor.settings.closed_scheduler_active.value || /^(?:[01]\d|2[0-3]):[0-5]\d$/.test(v) || 'Nem megfeleő formátum (hh:mm)'
            ]"
            bg-color="white"
          />
        </v-row>
        <v-row class="mb-2">
          <v-checkbox
            v-model="vendor.settings.closure_scheduler_active.value"
            color="primary"
            :label="vendor.settings.closure_scheduler_active.name"
            class="ms-2"
          />
          <v-text-field
            v-model="vendor.settings.closure_scheduler.value"
            :label="vendor.settings.closure_scheduler.name"
            :disabled="!vendor.settings.closure_scheduler_active.value"
            :rules="[
              v => !vendor.settings.closure_scheduler_active.value || !!v || 'Kötelező mező',
              v => !vendor.settings.closure_scheduler_active.value || /^(?:[01]\d|2[0-3]):[0-5]\d$/.test(v) || 'Nem megfeleő formátum (hh:mm)'
            ]"
            bg-color="white"
          />
        </v-row>
        <v-text-field
          v-model="vendor.settings.order_text_template.value"
          :label="vendor.settings.order_text_template.name"
          bg-color="white"
        />
        <h5 class="">
          Automatikus rendelés beállítások
        </h5>
        <hr class="mt-1">

        <v-checkbox
          v-model="vendor.settings.auto_email_order.value"
          class="ms-2"
          color="primary"
          :label="vendor.settings.auto_email_order.name"
          :disabled="!smtpStatus"
        />
        <v-text-field
          v-model="vendor.settings.email_order_scheduler.value"
          :label="vendor.settings.email_order_scheduler.name"
          :disabled="!vendor.settings.auto_email_order.value"
          :rules="[
            v => !vendor.settings.email_order_scheduler.value || !!v || 'Kötelező mező',
            v => !vendor.settings.email_order_scheduler.value || /^(?:[01]\d|2[0-3]):[0-5]\d$/.test(v) || 'Nem megfeleő formátum (hh:mm)'
          ]"
          bg-color="white"
        />
        <v-text-field
          v-model.number="vendor.settings.email_min_user.value"
          :label="vendor.settings.email_min_user.name"
          :rules="[
            v => !!v || v===0 || 'Kötelező mező',
            v => /^\d+$/.test(v) || 'Csak szám lehetséges'
          ]"
          type="number"
          :disabled="!vendor.settings.auto_email_order.value"
          bg-color="white"
          hint="A rendelés csak abban az esetben lesz elküldve ha legalább ennyi felhasználó résztvesz a rendelésben."
        />
        <v-combobox
          v-model="vendor.settings.auto_email_order_to.value"

          chips
          multiple
          :label="vendor.settings.auto_email_order_to.name"
          :disabled="!vendor.settings.auto_email_order.value"
          :rules="[ v => validateEmails(v,vendor.settings.auto_email_order.value)]"
          bg-color="white"
        >
          <template #chip="{ props }">
            <v-chip
              v-bind="props"
              closable
            />
          </template>
        </v-combobox>
        <v-combobox
          v-model="vendor.settings.auto_email_order_cc.value"

          chips
          multiple
          :label="vendor.settings.auto_email_order_cc.name"
          :disabled="!vendor.settings.auto_email_order.value"
          :rules="[validateEmails]"
          bg-color="white"
        >
          <template #chip="{ props }">
            <v-chip
              v-bind="props"
              closable
            />
          </template>
        </v-combobox>
        <v-text-field
          v-model="vendor.settings.auto_email_subject.value"
          :label="vendor.settings.auto_email_subject.name"
          :disabled="!vendor.settings.auto_email_order.value"
          bg-color="white"
        />
        <v-textarea
          v-model="vendor.settings.auto_email_order_template.value"
          :label="vendor.settings.auto_email_order_template.name"

          bg-color="white"
        />
        <v-btn
          class="bg-primary mt-1"
          type="button"
          name="save"
          @click="saveSettings()"
        >
          Mentés
        </v-btn>
      </v-form>
    </v-container>
  </div>
</template>

<script>
import { useVendorStore } from "@/stores/vendor";
import { useAuth } from "@/stores/auth";
import { ref } from 'vue';
import axios from "axios";

export default {
    name: "VendorSettings",
    setup() {
      const auth = useAuth();
      const vendorStore = useVendorStore();
      const form = ref()
      return {
        auth,
        vendorStore,
        form
      }
    },
    data() {
      return {
        vendor: {},
        isLoading: true,
        smtpStatus: false
      }
    },
    mounted() {
      this.getSettings()
    },
    methods: {
      getSettings: function () {
        this.vendorStore.fetchVendor(this.$route.params.id)
          .then(response => {
            this.vendor = response.data.data
            this.isLoading = false;

          })
        axios.get(`http://${window.location.host}/api/setting/get/smtp_address`)
          .then(response => {
            if (response.status === 200 && response.data.smtp_address !== "") {
              this.smtpStatus = true
            }
          })

      },
      saveSettings: async function () {
        const { valid } = await this.$refs.form.validate()

        if (valid) {
          this.vendorStore.saveSettings(this.$route.params.id, this.vendor.settings)
          .then(response => {
            this.settings = response.data
          })
        }
      },
      async validateForm() {
        const { valid } = await this.$refs.form.validate()

        if (valid) {
          alert("Form submitted successfully! 🎉");
        } else {
          alert("Please fix the errors before submitting.");
        }
      },
      validateEmails(value, required=false) {
        if (required && (!value || value.length === 0)) {
          return "At least one email is required.";
        }

        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const invalidEmails = value.filter(email => !emailPattern.test(email));

        if (invalidEmails.length > 0) {
          return `Invalid emails: ${invalidEmails.join(", ")}`;
        }

        return true;
      }
    }
};
</script>

<style scoped>
</style>
