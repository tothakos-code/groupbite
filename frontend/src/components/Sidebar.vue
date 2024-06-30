<template>
  <div
    class="sidebar col p-0"
    :class="['bg-' + auth.getUserColor ]"
  >
    <div class="col row p-0 m-0 d-flex flex-column flex-fill h-100 justify-content-center align-items-start">
      <ul class="list-group flex-fill p-0">
        <router-link
          to="/home"
          class="list-group-item border rounded rounded-circle mt-2 mx-auto p-0 position-relative"

          style="width: 3rem; height: 3rem;"
          :style="'background-color: ' + backgroundColor('Home', 30, 80) + ';'"
          :onmouseover="'this.style.backgroundColor=\'' + backgroundColor('Home', 30, 70)+'\''"
          :onmouseout="'this.style.backgroundColor=\'' + backgroundColor('Home', 30, 80)+'\''"
          title="Home"
        >
          <span class="position-absolute top-50 start-50 translate-middle text-dark">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="28"
              height="28"
              fill="currentColor"
              class="bi bi-house"
              viewBox="0 0 16 16"
            >
              <path d="M8.707 1.5a1 1 0 0 0-1.414 0L.646 8.146a.5.5 0 0 0 .708.708L2 8.207V13.5A1.5 1.5 0 0 0 3.5 15h9a1.5 1.5 0 0 0 1.5-1.5V8.207l.646.647a.5.5 0 0 0 .708-.708L13 5.793V2.5a.5.5 0 0 0-.5-.5h-1a.5.5 0 0 0-.5.5v1.293zM13 7.207V13.5a.5.5 0 0 1-.5.5h-9a.5.5 0 0 1-.5-.5V7.207l5-5z" />
            </svg>
          </span>
        </router-link>
        <router-link
          v-for="vendor in vendors"
          :key="vendor.name"
          class="list-group-item border rounded rounded-circle mt-2 mx-auto p-0 position-relative"
          :class="(selectedVendor && selectedVendor.id === vendor.id) ? 'border-3' : ''"
          style="width: 3rem; height: 3rem;"
          :style="'background-color: ' + backgroundColor(vendor.name, 30, 80) + ';'"
          :onmouseover="'this.style.backgroundColor=\'' + backgroundColor(vendor.name, 30, 70)+'\''"
          :onmouseout="'this.style.backgroundColor=\'' + backgroundColor(vendor.name, 30, 80)+'\''"
          :title="vendor.name"
          :to="'/menu/'+vendor.name"
        >
          <span class="fs-4 position-absolute top-50 start-50 translate-middle text-dark">
            {{ firstChar(vendor.name) }}
          </span>
        </router-link>
      </ul>
      <VersionInfo class=" d-flex flex-fill p-0 align-items-end justify-content-center mb-2" />
    </div>
  </div>
</template>
<script>
import { state } from "@/socket";
import VersionInfo from "@/components/VersionInfo.vue"
import { useAuth } from "@/stores/auth";

export default {
  name: 'SidebarMenu',
  components: {
    VersionInfo
  },
  setup(){
    const auth = useAuth()
    return {
      auth
    }
  },
  computed: {
    vendors() {
      return state.vendors;
    },
    selectedVendor() {
      return state.selected_vendor;
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
