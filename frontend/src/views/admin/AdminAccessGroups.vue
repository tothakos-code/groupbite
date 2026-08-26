<template>
  <v-container fluid>
    <v-row
      align="center"
      class="mb-2"
    >
      <v-col>
        <h2 class="text-h5 font-weight-bold">
          <v-icon class="me-2">
            mdi-account-multiple
          </v-icon>
          Csoportok
        </h2>
        <p class="text-body-2 text-grey">
          Egy csoport tagjai a csoporthoz rendelt üzletek adminisztrátori jogosultságát kapják meg
          (menü, készlet, rendelések, statisztika, beállítások — az adott üzletre szűkítve).
        </p>
      </v-col>
      <v-col cols="auto">
        <v-btn
          color="primary"
          prepend-icon="mdi-plus"
          @click="createDialog = true"
        >
          Új csoport
        </v-btn>
      </v-col>
    </v-row>

    <div
      v-if="loading"
      class="text-center py-8"
    >
      <v-progress-circular
        indeterminate
        color="primary"
      />
    </div>

    <div
      v-else-if="groups.length === 0"
      class="text-center text-grey py-8"
    >
      Még nincs egyetlen csoport sem.
    </div>

    <v-row v-else>
      <v-col
        v-for="group in groups"
        :key="group.id"
        cols="12"
        md="6"
      >
        <v-card
          variant="outlined"
          elevation="1"
        >
          <v-card-title class="d-flex align-center bg-grey-lighten-5">
            <span class="flex-grow-1">{{ group.name }}</span>
            <v-btn
              icon="mdi-delete"
              size="small"
              variant="text"
              color="error"
              @click="deleteGroup(group)"
            />
          </v-card-title>
          <v-card-text>
            <div class="text-caption text-grey mb-1">
              Tagok
            </div>
            <div class="mb-3">
              <v-chip
                v-for="member in group.members"
                :key="member.id"
                size="small"
                closable
                class="me-1 mb-1"
                @click:close="removeMember(group, member)"
              >
                {{ member.username }}
              </v-chip>
              <v-menu>
                <template #activator="{ props }">
                  <v-chip
                    v-bind="props"
                    size="small"
                    variant="outlined"
                    prepend-icon="mdi-plus"
                    class="mb-1"
                  >
                    Tag hozzáadása
                  </v-chip>
                </template>
                <v-list density="compact">
                  <v-list-item
                    v-for="user in availableUsers(group)"
                    :key="user.id"
                    :title="user.username"
                    @click="addMember(group, user)"
                  />
                  <v-list-item
                    v-if="availableUsers(group).length === 0"
                    title="Nincs több felhasználó"
                    disabled
                  />
                </v-list>
              </v-menu>
            </div>

            <div class="text-caption text-grey mb-1">
              Üzletek
            </div>
            <div>
              <v-chip
                v-for="vendor in group.vendors"
                :key="vendor.id"
                size="small"
                color="primary"
                variant="tonal"
                closable
                class="me-1 mb-1"
                @click:close="removeVendor(group, vendor)"
              >
                {{ vendor.name }}
              </v-chip>
              <v-menu>
                <template #activator="{ props }">
                  <v-chip
                    v-bind="props"
                    size="small"
                    variant="outlined"
                    prepend-icon="mdi-plus"
                    class="mb-1"
                  >
                    Üzlet hozzáadása
                  </v-chip>
                </template>
                <v-list density="compact">
                  <v-list-item
                    v-for="vendor in availableVendors(group)"
                    :key="vendor.id"
                    :title="vendor.name"
                    @click="addVendor(group, vendor)"
                  />
                  <v-list-item
                    v-if="availableVendors(group).length === 0"
                    title="Nincs több üzlet"
                    disabled
                  />
                </v-list>
              </v-menu>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog
      v-model="createDialog"
      max-width="400"
    >
      <v-card>
        <v-card-title>Új csoport</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="newGroupName"
            label="Csoport neve"
            autofocus
            @keyup.enter="createGroup"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="createDialog = false"
          >
            Mégse
          </v-btn>
          <v-btn
            color="primary"
            variant="tonal"
            :disabled="!newGroupName"
            @click="createGroup"
          >
            Létrehozás
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AdminAccessGroups',
  data() {
    return {
      loading: false,
      groups: [],
      allUsers: [],
      allVendors: [],
      createDialog: false,
      newGroupName: '',
    };
  },
  async mounted() {
    await this.loadAll();
  },
  methods: {
    async loadAll() {
      this.loading = true;
      try {
        const [groupsRes, usersRes, vendorsRes] = await Promise.all([
          axios.get('/api/access-groups'),
          axios.get('/api/user/', { params: { limit: 1000, page: 1 } }),
          axios.get('/api/vendor'),
        ]);
        this.groups = groupsRes.data.data;
        this.allUsers = usersRes.data.data.items;
        this.allVendors = vendorsRes.data.data;
      } catch (e) {
        console.error('Failed to load access groups:', e);
      } finally {
        this.loading = false;
      }
    },

    availableUsers(group) {
      const memberIds = new Set(group.members.map(m => m.id));
      return this.allUsers.filter(u => !memberIds.has(u.id));
    },

    availableVendors(group) {
      const vendorIds = new Set(group.vendors.map(v => v.id));
      return this.allVendors.filter(v => !vendorIds.has(v.id));
    },

    async createGroup() {
      if (!this.newGroupName) return;
      try {
        const res = await axios.post('/api/access-groups', { data: { name: this.newGroupName } });
        this.groups.push(res.data.data);
        this.newGroupName = '';
        this.createDialog = false;
      } catch (e) {
        console.error('Failed to create group:', e);
      }
    },

    async deleteGroup(group) {
      try {
        await axios.delete(`/api/access-groups/${group.id}`);
        this.groups = this.groups.filter(g => g.id !== group.id);
      } catch (e) {
        console.error('Failed to delete group:', e);
      }
    },

    async addMember(group, user) {
      try {
        await axios.post(`/api/access-groups/${group.id}/members`, { data: { user_id: user.id } });
        group.members.push({ id: user.id, username: user.username });
      } catch (e) {
        console.error('Failed to add member:', e);
      }
    },

    async removeMember(group, member) {
      try {
        await axios.delete(`/api/access-groups/${group.id}/members/${member.id}`);
        group.members = group.members.filter(m => m.id !== member.id);
      } catch (e) {
        console.error('Failed to remove member:', e);
      }
    },

    async addVendor(group, vendor) {
      try {
        await axios.post(`/api/access-groups/${group.id}/vendors`, { data: { vendor_id: vendor.id } });
        group.vendors.push({ id: vendor.id, name: vendor.name });
      } catch (e) {
        console.error('Failed to add vendor:', e);
      }
    },

    async removeVendor(group, vendor) {
      try {
        await axios.delete(`/api/access-groups/${group.id}/vendors/${vendor.id}`);
        group.vendors = group.vendors.filter(v => v.id !== vendor.id);
      } catch (e) {
        console.error('Failed to remove vendor:', e);
      }
    },
  },
};
</script>
