<template>
  <v-container
    max-width="560"
    class="mt-6"
  >
    <h1 class="mb-6">
      {{ $t('vendor.add.title') }}
    </h1>

    <v-form
      ref="form"
      @submit.prevent="createVendor"
    >
      <v-text-field
        v-model="vendor.name"
        :label="$t('vendor.add.name')"
        prepend-icon="mdi-store"
        variant="outlined"
        density="comfortable"
        :rules="[v => !!v || 'Kötelező mező']"
        class="mb-2"
      />

      <v-select
        v-model="vendor.menu_type"
        :label="$t('vendor.menu_type.label')"
        :items="menuTypeOptions"
        item-title="label"
        item-value="value"
        prepend-icon="mdi-menu"
        variant="outlined"
        density="comfortable"
        class="mb-2"
      />

      <v-select
        v-model="vendor.plugin_id"
        :label="$t('vendor.plugin.label')"
        :items="pluginOptions"
        item-title="label"
        item-value="value"
        prepend-icon="mdi-puzzle"
        variant="outlined"
        density="comfortable"
        clearable
        :loading="loadingPlugins"
        class="mb-4"
      />

      <v-btn
        type="submit"
        color="primary"
        :loading="vendorStore.isLoading"
        block
      >
        {{ $t('vendor.add.save') }}
      </v-btn>
    </v-form>
  </v-container>
</template>

<script>
import { useVendorStore } from '@/stores/vendor'

export default {
  name: 'VendorAdd',
  setup() {
    const vendorStore = useVendorStore()
    return { vendorStore }
  },
  data() {
    return {
      vendor: {
        name: '',
        menu_type: 'fixed_menu',
        plugin_id: null,
      },
      plugins: [],
      loadingPlugins: false,
      menuTypeOptions: [
        { value: 'fixed_menu',    label: this.$t('vendor.menu_type.fixed_menu')    },
        { value: 'daily_menu',    label: this.$t('vendor.menu_type.daily_menu')    },
        { value: 'own_inventory', label: this.$t('vendor.menu_type.own_inventory') },
      ],
    }
  },
  computed: {
    pluginOptions() {
      const none = [{ value: null, label: this.$t('vendor.plugin.none') }]
      return none.concat(this.plugins.map(p => ({ value: p.id, label: p.id })))
    },
  },
  async mounted() {
    this.loadingPlugins = true
    try {
      const response = await this.vendorStore.fetchPlugins()
      if (response?.status === 200) this.plugins = response.data.data
    } finally {
      this.loadingPlugins = false
    }
  },
  methods: {
    async createVendor() {
      const { valid } = await this.$refs.form.validate()
      if (!valid) return
      const response = await this.vendorStore.add({
        name: this.vendor.name,
        menu_type: this.vendor.menu_type,
        plugin_id: this.vendor.plugin_id || null,
      })
      if (response?.status === 200) this.$router.push(`/admin/${response.data.data.id}/config`)
    },
  },
}
</script>
