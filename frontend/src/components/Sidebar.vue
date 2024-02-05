<template>
  <div class="sidebar col bg-falusi p-0">
    <div class="p-0 m-0 align-items-start">
      <ul class="list-group">
        <a
          v-for="(vendor_obj, vendor_name) in vendors"
          :key="vendor_name"
          class="list-group-item border rounded rounded-circle p-auto mt-2 mx-auto"
          style="width: 3rem; height: 3rem;"
          :style="'background-color: ' + backgroundColor(vendor_obj.name, 30, 80) + ';'"
          :onmouseover="'this.style.backgroundColor=\'' + backgroundColor(vendor_obj.name, 30, 70)+'\''"
          :onmouseout="'this.style.backgroundColor=\'' + backgroundColor(vendor_obj.name, 30, 80)+'\''"
          :title="vendor_obj.name"
          @click="switchVendor(vendor_obj.name)"
        >
          <span class="text fs-4 text-center text-truncate m-auto">
            {{ firstChar(vendor_obj.name) }}
          </span>
        </a>
      </ul>
    </div>
  </div>
</template>

<script>

export default {
  name: 'SidebarMenu',
  data() {
    return {
      vendors: {}
    };
  },
  mounted() {
    this.fetch_vendors();
  },
  methods: {
    fetch_vendors: function() {
      fetch(`http://${window.location.host}/api/get_vendors`,{
        method: "GET",
      })
        .then(response => response.json())
          .then(data => {
            this.vendors = data;
            for (const [key, value] of Object.entries(this.vendors)) {
              value.configuration = JSON.parse(value.configuration);
              value.component = import("@/../../plugins/falusi/frontend/App.vue")
              console.log(key, value);
            }

          })
        .catch(error => console.error('Error fecthing vendors:',error));
    },
    firstChar: function(string) {
      return string.charAt(0);
    },
    switchVendor: function(vendorId) {
      alert(vendorId)
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
