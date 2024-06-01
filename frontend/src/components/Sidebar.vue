<template>
  <div class="sidebar col bg-falusi p-0">
    <div class="col row p-0 m-0 d-flex flex-column flex-fill h-100 justify-content-center align-items-start">
      <ul class="list-group flex-fill p-0">
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
      <VersionInfo class=" d-flex flex-fill p-0 align-items-end justify-content-center mb-2" />
    </div>
  </div>
</template>
<!-- ToDo: update router-link to change the seleted_vendor -->
<script>
import { state } from "@/socket";
import VersionInfo from "@/components/VersionInfo.vue"

export default {
  name: 'SidebarMenu',
  components: {
    VersionInfo
  },
  computed: {
    vendors() {
      return state.vendors;
    }
  },
  methods: {
    firstChar: function(string) {
      return string.charAt(0);
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
