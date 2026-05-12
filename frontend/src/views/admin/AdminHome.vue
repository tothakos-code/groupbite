<template>
  <div class="admin-layout">
    <!-- Left Sidebar -->
    <nav
      class="admin-nav"
      :class="{ 'admin-nav--collapsed': navCollapsed }"
    >
      <div class="nav-header">
        <span
          v-if="!navCollapsed"
          class="nav-title"
        >Adminisztráció</span>
        <v-btn
          :icon="navCollapsed ? 'mdi-chevron-right' : 'mdi-chevron-left'"
          variant="text"
          size="small"
          @click="navCollapsed = !navCollapsed"
        />
      </div>

      <v-list
        density="compact"
        nav
        class="nav-list"
      >
        <v-tooltip
          v-for="item in menuItems"
          :key="item.path"
          :text="item.label"
          :disabled="!navCollapsed"
          location="right"
        >
          <template #activator="{ props }">
            <v-list-item
              v-bind="props"
              :active="isActive(item.path)"
              :color="item.color"
              rounded="lg"
              class="nav-item"
              @click="navigate(item.path)"
            >
              <template #prepend>
                <v-icon :color="isActive(item.path) ? item.color : ''">
                  {{ item.icon }}
                </v-icon>
              </template>
              <v-list-item-title
                v-if="!navCollapsed"
                class="nav-item-title"
              >
                {{ item.label }}
              </v-list-item-title>
            </v-list-item>
          </template>
        </v-tooltip>
      </v-list>

      <!-- Back button pinned to bottom -->
      <div class="nav-footer">
        <v-divider class="mb-3" />
        <v-tooltip
          text="Vissza"
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
              @click="navigateBack"
            >
              <v-icon :start="!navCollapsed">
                mdi-arrow-left
              </v-icon>
              <span v-if="!navCollapsed">Vissza</span>
            </v-btn>
          </template>
        </v-tooltip>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="admin-content">
      <router-view />
    </main>
  </div>
</template>

<script>
import { useAuth } from '@/stores/auth'
import { useVendorStore } from '@/stores/vendor'

export default {
  name: 'AdminView',
  setup() {
    const auth = useAuth()
    const vendorStore = useVendorStore()
    return { auth, vendorStore }
  },
  data() {
    return {
      navCollapsed: !!this.$route?.params?.id,
      menuItems: [
        { label: 'Üzlet kezelő',  path: '/admin/vendors',  icon: 'mdi-store',          color: 'primary' },
        { label: 'Felhasználók',  path: '/admin/users',    icon: 'mdi-account-group',  color: 'primary' },
        { label: 'Rendelések',    path: '/admin/orders',   icon: 'mdi-clipboard-list', color: 'primary' },
        { label: 'Pluginok',      path: '/admin/plugins',  icon: 'mdi-puzzle',         color: 'primary' },
        { label: 'Beállítások',   path: '/admin/settings', icon: 'mdi-cog',            color: 'primary' },
      ],
    }
  },
  watch: {
    '$route'(to) {
      if (to.params.id) {
        this.navCollapsed = true
      }
    },
  },
  methods: {
    isActive(path) {
      return this.$route.path.startsWith(path)
    },
    navigate(path) {
      this.vendorStore.selectedVendor = undefined
      this.$router.push({ path })
    },
    navigateBack() {
      this.vendorStore.selectedVendor = undefined
      window.history.back()
    },
  },
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  height: calc(100vh - 64px); /* adjust to your app toolbar height */
  overflow: hidden;
}

/* ── Sidebar ─────────────────────────────────────────── */
.admin-nav {
  display: flex;
  flex-direction: column;
  width: 220px;
  min-width: 220px;
  background: rgb(var(--v-theme-surface));
  border-right: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  transition: width 0.25s ease, min-width 0.25s ease;
  overflow: hidden;
}

.admin-nav--collapsed {
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
.admin-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}

/* ── Mobile ──────────────────────────────────────────── */
@media (max-width: 768px) {
  .admin-nav {
    width: 64px;
    min-width: 64px;
  }
}
</style>
