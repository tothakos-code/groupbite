<template>
  <v-list>
    <v-list-item
      link
      class="p-0 d-flex justify-content-center"
      @click="goto('/home/')"
    >
      <v-avatar
        size="40"
        :style="'background-color: ' + backgroundColor('Home', 30, 80) + ';'"
        :onmouseover="'this.style.backgroundColor=\'' + backgroundColor('Home', 30, 70)+'\''"
        :onmouseout="'this.style.backgroundColor=\'' + backgroundColor('Home', 30, 80)+'\''"
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
      </v-avatar>
    </v-list-item>


    <v-list-item

      v-for="vendor in vendors"
      :key="vendor.name"
      link
      class="p-0 d-flex justify-content-center"
      @click="goto('/menu/'+vendor.name+'/'+new Date().toISODate())"
    >
      <v-avatar

        size="40"
        :class="(selectedVendor && selectedVendor.id === vendor.id) ? 'border-3' : ''"
        :style="'background-color: ' + backgroundColor(vendor.name, 30, 80) + ';'"
        :onmouseover="'this.style.backgroundColor=\'' + backgroundColor(vendor.name, 30, 70)+'\''"
        :onmouseout="'this.style.backgroundColor=\'' + backgroundColor(vendor.name, 30, 80)+'\''"
      >
        <span class="fs-4 position-absolute top-50 start-50 translate-middle text-dark">
          {{ firstChar(vendor.name) }}
        </span>
      </v-avatar>
    </v-list-item>
    <v-list />
  </v-list>
</template>
<script>

import { useAuth } from "@/stores/auth";
import { useVendorStore } from "@/stores/vendor";

export default {
  name: "SidebarMenu",

  setup(){
    const auth = useAuth()
    const vendorStore = useVendorStore()
    return {
      auth,
      vendorStore
    }
  },
  computed: {
    vendors() {
      return this.vendorStore.vendors;
    },
    selectedVendor() {
      return this.vendorStore.selectedVendor;
    },
  },
  methods: {
    firstChar: function(string) {
      return string.charAt(0);
    },
    goto(path) {
      this.$router.push({ path: path})
    },
    backgroundColor: function(str, s, l) {

      var hash = 0;
      for (var i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
      }

      var h = hash % 360;
      return "hsl("+h+", "+s+"%, "+l+"%)";

    }
  }
}
</script>

<style>

</style>
