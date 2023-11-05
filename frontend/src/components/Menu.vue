<template>
  <div class="card">
    <div class="card-header row d-flex px-2">
      <div class="col-3 col-md-6 col-lg-8 row px-0">
        <div class="col-12 col-lg-4 my-auto">
          <h2 class="">Étlap</h2>
        </div>
        <div class="col-0 d-none col-lg-8 d-lg-inline my-auto truncate">
          <TransferPopup/>
        </div>
      </div>
      <div class="col-9 col-md-6 col-lg-4 d-flex flex-fill px-0">
        <Datestamp @selectedDate="(day) => this.getMenu(day)" :limitToCurrentWeek="true"/>
      </div>
    </div>
    <div class="row col list-group">
      <div class="col">
        <div class="list-group my-1">
          <MenuItem
            v-for="item in items"
            :key="item.id"
            :item="item">
          </MenuItem>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Datestamp from './DateStamp.vue'
import MenuItem from './MenuItem.vue'
import { state } from "@/socket";
import { useAuth } from "@/auth";
import TransferPopup from './TransferPopup.vue'



export default {
  name: 'FalusiMenu',
  components: {
    TransferPopup,
    Datestamp,
    MenuItem
  },
  setup() {
    const auth = useAuth();
    return {
      auth
    }
  },
  mounted() {
    this.getMenu();
  },
  methods: {
    getMenu: function(day) {
      let url = ''
      if (day === undefined) {
        url = `http://${window.location.host}/api/menu/get/${new Date().toISOString().split('T')[0]}`
      } else {
        url = `http://${window.location.host}/api/menu/get/${new Date(day).toISOString().split('T')[0]}`
      }

      fetch(url)
        .then(response => response.json())
          .then(data => {
            this.items = data;
          })
        .catch(error => console.error(error));
    }
  },
  data() {
    return {
      items: []
    }
  },
  computed: {
    }
  }
}
</script>

<style>
[data-bs-theme=light] .list-group-item:hover {
  background-color: lightgray;
}
[data-bs-theme=dark] .list-group-item:hover {
  background-color: #3c3c3c;
}
</style>
