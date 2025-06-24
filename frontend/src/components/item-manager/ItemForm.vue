<template>
  <v-container
    fluid
    class="pa-4"
  >
    <v-card
      elevation="2"
      class="mx-auto"
    >
      <v-card-title class="text-h6 bg-primary text-white">
        <v-row
          align="center"
          no-gutters
        >
          <v-col>
            <h2 class="text-h6 font-weight-bold">
              <v-icon class="me-2">
                mdi-plus
              </v-icon>
              Új étel hozzáadása
            </h2>
          </v-col>
        </v-row>
      </v-card-title>

      <v-card-text class="pa-4">
        <v-form
          ref="form"
          @submit.prevent="submit"
        >
          <v-row>
            <v-col
              cols="12"
              md="3"
            >
              <v-text-field
                v-model="localItem.name"
                label="Név"
                variant="outlined"
                density="comfortable"
                :rules="[rules.required]"
                required
              />
            </v-col>

            <v-col
              cols="12"
              md="4"
            >
              <v-text-field
                v-model="localItem.description"
                label="Leírás"
                variant="outlined"
                density="comfortable"
              />
            </v-col>

            <v-col
              cols="12"
              md="3"
            >
              <v-text-field
                v-model="localItem.category"
                label="Kategória"
                variant="outlined"
                density="comfortable"
                :rules="[rules.required]"
                required
              />
            </v-col>

            <v-col
              cols="12"
              md="2"
              class="d-flex align-top"
            >
              <v-btn
                type="submit"
                color="primary"
                size="large"
                :loading="loading"
                :disabled="!isFormValid"
                block
              >
                <v-icon class="me-2">
                  mdi-plus
                </v-icon>
                Hozzáadás
              </v-btn>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
export default {
  name: "ItemForm",
  props: {
    modelValue: {
      type: Object,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue', 'submit'],
  data() {
    return {
      rules: {
        required: value => !!value || 'Ez a mező kötelező'
      }
    }
  },
  computed: {
    localItem: {
      get() {
        return this.modelValue;
      },
      set(value) {
        this.$emit('update:modelValue', value);
      }
    },
    isFormValid() {
      return this.localItem.name && this.localItem.category;
    }
  },
  methods: {
    async submit() {
      const { valid } = await this.$refs.form.validate();
      if (valid) {
        this.$emit('submit');
      }
    }
  }
};
</script>

<style scoped>
.v-card {
  border-radius: 12px !important;
}
</style>
