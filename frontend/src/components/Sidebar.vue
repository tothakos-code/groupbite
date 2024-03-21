<template>
  <div class="sidebar col bg-falusi p-0">
    <div class="p-0 m-0 align-items-start">
      <ul class="list-group">
        <router-link
          to="/home"
          class="list-group-item border rounded rounded-circle p-auto mt-2 mx-auto"
          style="width: 3rem; height: 3rem;"
          :style="'background-color: ' + backgroundColor('Home', 30, 80) + ';'"
          :onmouseover="'this.style.backgroundColor=\'' + backgroundColor('Home', 30, 70)+'\''"
          :onmouseout="'this.style.backgroundColor=\'' + backgroundColor('Home', 30, 80)+'\''"
          title="Home"
        >
          <span class="text fs-4 text-center text-truncate m-auto">
            H
          </span>
        </router-link>
        <router-link
          v-for="vendor in vendors"
          :key="vendor.name"
          class="list-group-item border rounded rounded-circle p-auto mt-2 mx-auto"
          style="width: 3rem; height: 3rem;"
          :style="'background-color: ' + backgroundColor(vendor.name, 30, 80) + ';'"
          :onmouseover="'this.style.backgroundColor=\'' + backgroundColor(vendor.name, 30, 70)+'\''"
          :onmouseout="'this.style.backgroundColor=\'' + backgroundColor(vendor.name, 30, 80)+'\''"
          :title="vendor.name"
          :to="'/menu/'+vendor.name"
        >
          <span class="text fs-4 text-center text-truncate m-auto">
            {{ firstChar(vendor.name) }}
          </span>
        </router-link>
      </ul>
    </div>
  </div>
</template>
<!-- ToDo: update router-link to change the seleted_vendor -->
<script>
import { state } from "@/socket";

export default {
  name: 'SidebarMenu',
  computed: {
    vendors() {
      return state.vendors;
    }
  },
  methods: {
    firstChar: function(string) {
      return string.charAt(0);
    },
    setVendor: function(vendor_id) {
      state.selected_vendor = vendor_id
    },
    backgroundColor: function(str, s, l) {

      var hash = 0;
      for (var i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
      }

      var h = hash % 360;
      return 'hsl('+h+', '+s+'%, '+l+'%)';

    }
  }
}
</script>

<style>
.sidebar {
  max-width: 65px !important;
}
</style>
