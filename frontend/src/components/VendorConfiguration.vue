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
import { ref } from "vue"
import VendorSettings from "./VendorSettings.vue"
import VendorMenuManager from "./VendorMenuManager.vue"

export default {
    name: "VendorConfiguration",
    setup() {
      const activeTab = ref("Settings")
      const allTabs = {
        "Settings": VendorSettings,
        "Menus": VendorMenuManager,
      }
      return {
        activeTab,
        allTabs
      }
    },
};
</script>

<style scoped>

</style>
