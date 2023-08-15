<template>
  <div class="card">
    <div class="card-header row d-flex">
      <div class="col-6">
        <h2 class="ps-0">Étlap</h2>
      </div>
      <div class="col-6">
        <Datestamp @selectedDate="(day) => this.getMenu(day)" :limitToCurrentWeek="true"/>
      </div>
    </div>
    <div class="row">
      <div class="col">
        <div class="list-group">
          <MenuItem
            v-for="item in items"
            :key="item.id"
            :item="item"
            class="list-group-item">
          </MenuItem>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useCookies } from "vue3-cookies";
import Datestamp from './DateStamp.vue'
import MenuItem from './MenuItem.vue'
import { state } from "@/socket";


export default {
  name: 'FalusiMenu',
  components: {
    Datestamp,
    MenuItem
  },
  setup() {
    const { cookies } = useCookies();
    return { cookies };
  },
  mounted() {
    this.getMenu();
  },
  methods: {
    getMenu: function(day) {
      let url = ''
      if (day === undefined) {
        url = `http://${window.location.hostname}/api/menu/get`
      } else {
        url = `http://${window.location.hostname}/api/menu/get/${new Date(day).toISOString().split('T')[0]}`
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
    usercolor() {
        return state.user.ui_color ? state.user.ui_color : "falusi";
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
