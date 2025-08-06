<template>
  <v-container
    fluid
    class="pa-4"
  >
    <v-card
      elevation="2"
      class="mx-auto"
    >
      <v-card-title class="bg-primary text-white ">
        <v-row
          align="center"
          no-gutters
        >
          <v-col>
            <h2 class="text-h6 font-weight-bold">
              <v-icon class="me-2">
                mdi-magnify
              </v-icon>
              Keresés
            </h2>
          </v-col>
        </v-row>
      </v-card-title>

      <v-card-text class="pa-4">
        <v-form @submit.prevent="search">
          <v-row>
            <v-col
              cols="12"
              md="8"
            >
              <v-text-field
                v-model="searchValue"
                label="Keresés név, leírás vagy kategória alapján..."
                variant="outlined"
                density="comfortable"
                clearable
                prepend-inner-icon="mdi-magnify"
                @keyup.enter="search"
                @click:clear="clearSearch"
              />
            </v-col>

            <v-col
              cols="12"
              md="4"
              class="d-flex gap-2 align-top"
            >
              <v-btn
                type="submit"
                color="primary"
                variant="elevated"
                size="large"
              >
                <v-icon class="me-2">
                  mdi-magnify
                </v-icon>
                Keresés
              </v-btn>

              <v-btn
                v-if="searchValue"
                color="danger"
                variant="outlined"
                size="large"
                @click="clearSearch"
              >
                <v-icon class="me-2">
                  mdi-close
                </v-icon>
                Törlés
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
  name: "SearchForm",
  props: {
    modelValue: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue', 'search'],
  computed: {
    searchValue: {
      get() {
        return this.modelValue;
      },
      set(value) {
        this.$emit('update:modelValue', value);
      }
    }
  },
  methods: {
    search() {
      this.$emit('search');
    },
    clearSearch() {
      this.searchValue = '';
      this.$emit('search');
    }
  }
};
</script>

<style>
.v-card {
  border-radius: 12px !important;
}
</style>
