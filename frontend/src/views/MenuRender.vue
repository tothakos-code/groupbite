<template>
  <component
    :is="activeVendor"
    :key="activeVendorId"
  />
</template>

<script>
import Menu from '@/views/Menu.vue';
import { state } from "@/socket";
import { defineAsyncComponent } from 'vue';
// import axios from 'axios';

const PluginMenu = defineAsyncComponent({
  loader: () => import(`./../../../plugins/${state.selected_vendor.name}/frontend/App.vue`),
})

export default {
  name: 'MenuRenderView',
  components: {
    Menu,
    PluginMenu
  },
  beforeRouteEnter(to) {
    state.vendors.forEach((item) => {
      if (item.name === to.name || item.name+'-dated' === to.name) {
        state.selected_vendor = item;
      }
    });
    let today = new Date()
    if (to.params.selected_date === undefined) {
      if (today.getHours() >= 13) {
        state.selectedDate.setDate(today.getDate() + 1);
      } else {

        state.selectedDate.setDate(today.getDate());
      }
      history.pushState({}, "", `${to.path}`)
    } else {
      if (new Date(to.params.selected_date).getWeek() !== today.getWeek()) {
        state.selectedDate = today;
        history.pushState({}, "", `${to.path}`)
      } else {
        if (new Date(to.params.selected_date).getDate() === today.getDate()) {
          history.pushState({}, "", `${to.path}`)
        } else {
          state.selectedDate = new Date(to.params.selected_date);
          history.pushState({}, "", `${to.path}/${state.selectedDate.toISODate()}`)
        }
      }
    }
  },
  beforeRouteUpdate(to) {
    if (to.params.selected_date === undefined) {
      state.selectedDate = new Date();
    } else {
      state.selectedDate = new Date(to.params.selected_date);
    }
  },
  setup() {
    return {
      PluginMenu
    }
  },
  computed:{
    activeVendor() {
      return state.selected_vendor.type === 'basic' ? Menu : PluginMenu;
    },
    activeVendorId() {
      return state.selected_vendor.id;
    },
  },
};
</script>

<style scoped>
</style>
