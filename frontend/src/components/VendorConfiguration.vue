<template>
  <div class="row ms-2">
    <div class="">
      <ul class="nav nav-tabs">
        <li class="nav-item">
          <a
            class="nav-link text-groupbite"
            :class="{ 'active text-reset': activeTab === 'Settings'}"
            aria-current="page"
            href="#"
            @click="activeTab='Settings'"
          >Settings</a>
        </li>
        <li class="nav-item">
          <a
            class="nav-link text-groupbite"
            :class="{ 'active text-reset': activeTab === 'Menus'}"
            href="#"
            @click="activeTab='Menus'"
          >Menus</a>
        </li>
        <li class="nav-item">
          <a
            class="nav-link text-groupbite"
            :class="{ 'active text-reset': activeTab === 'Items'}"
            href="#"
            @click="activeTab='Items'"
          >Menu Items</a>
        </li>
      </ul>
    </div>
    <!-- <Transition
      name="fade"
    > -->
    <component :is="allTabs[activeTab]" />
    <!-- </Transition> -->
  </div>
</template>

<script>
import axios from 'axios';
import { useAuth } from '@/stores/auth';
import { notify } from "@kyvg/vue3-notification";
import { ref } from 'vue'
import VendorSettings from './VendorSettings.vue'
import VendorMenuManager from './VendorMenuManager.vue'
import VendorItemManager from './VendorItemManager.vue'

// use shallowRef to avoid component being deeply observed

export default {
    name: 'VendorConfiguration',
    setup() {
      const auth = useAuth();
      const activeTab = ref('Settings')
      const allTabs = {
        'Settings': VendorSettings,
        'Menus': VendorMenuManager,
        'Items': VendorItemManager,
      }
      return {
        auth,
        activeTab,
        allTabs
      }
    },
    data() {
      return {
        vendor: {}
      }
    },
    mounted() {
      this.getSettings()
    },
    methods: {
      getSettings: function () {
        axios.get(`http://${window.location.host}/api/vendor/${this.$route.params.id}/get`)
          .then(response => {
            this.vendor = response.data
          })
          .catch(e => {
              console.log(e);
          })
      },
      saveSettings: function () {
        axios.post(`http://${window.location.host}/api/vendor/${this.$route.params.id}/settings/save`, {'data':this.settings})
          .then(response => {
            this.settings = response.data
            notify({
              type: "info",
              text: "Beállítások mentése sikeres!",
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
    }
};
</script>

<style scoped>

</style>
