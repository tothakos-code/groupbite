<template>
  <component
    :is="activeVendor"
    :key="activeVendorId"
  />
</template>

<script>
import Menu from "@/views/menu/Menu.vue";
import { state } from "@/main";
import { defineAsyncComponent } from "vue";
import { useVendorStore } from "@/stores/vendor";


const PluginMenu = defineAsyncComponent({
  loader: () => import(`./../../../../plugins/${useVendorStore().selectedVendor.name}/frontend/App.vue`),
})

export default {
  name: "MenuRenderView",
  components: {
    Menu,
    PluginMenu
  },
  beforeRouteEnter(to) {
    useVendorStore().vendors.forEach((item) => {
      if (item.name === to.name || item.name+"-dated" === to.name) {
        useVendorStore().selectedVendor = item;
      }
    });
    let today = new Date()
    const urlDate = new Date(to.params.selected_date)
    if (to.params.selected_date === undefined) {
      state.selectedDate.setDate(today.getDate());
    } else {
      if (urlDate.getWeek() !== today.getWeek()) {
        state.selectedDate = today;
      } else {
        state.selectedDate = urlDate;
      }
    }
    history.pushState({}, "", `${to.path}/${state.selectedDate.toISODate()}`)
  },
  beforeRouteUpdate(to) {
    if (to.params.selected_date === undefined) {
      state.selectedDate = new Date();
    } else {
      state.selectedDate = new Date(to.params.selected_date);
    }
    history.pushState({}, "", `${to.path}/${state.selectedDate.toISODate()}`)
  },
  setup() {
    const vendorStore = useVendorStore();
    return {
      PluginMenu,
      vendorStore
    }
  },
  computed:{
    activeVendor() {
      return state.selectedVendor?.type === "plugin" ? PluginMenu : Menu;
    },
    activeVendorId() {
      return state.selectedVendor?.id;
    },
  },
};
</script>

<style scoped>
</style>
