<template>
  <div class="row ms-2">
    <div class="">
      <div
        class=""
      >
        <label for="name">
          Név:
          <input
            v-model="newMenu.name"
            type="text"
            name="name"
          >
        </label>
        <label for="freq">Menü gyakorisága:
          <select
            id="freq"
            v-model="newMenu.freq"
            name="freq"
          >
            <option value="FIX">Fix</option>
            <option value="DAILY">Napi</option>
            <option value="WEAKLY">Heti</option>
            <option value="MONTLY">Havi</option>
            <option value="YEARLY">Évi</option>
          </select>
        </label>
      </div>
      <button
        class="btn"
        :class="['btn-' + auth.userColor.value ]"
        type="button"
        name="save"
        @click="addMenu()"
      >
        Létrehoz
      </button>
    </div>
  </div>
  <div class="">
    <table class="table table-striped table-hover">
      <thead>
        <tr>
          <th scope="col">
            #
          </th>
          <th scope="col">
            Név
          </th>
          <th scope="col">
            Dátum
          </th>
          <th scope="col">
            Gyakoriság
          </th>
        </tr>
      </thead>
      <tbody class="table-group-divider">
        <tr
          v-for="menu,i in menulist"
          :key="i"
        >
          <th scope="row">
            {{ menu.id }}
          </th>
          <td>
            {{ menu.name }}
          </td>
          <td>
            {{ menu.menu_date }}
          </td>
          <td>
            {{ menu.freq }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from 'axios';
import { useAuth } from '@/auth';

export default {
    name: 'PluginConfiguration',
    props: {
      id:{
        type: String,
        required: true
      },
    },
    setup() {
      const auth = useAuth();
      return {
        auth
      }
    },
    data() {
      return {
        menulist: [],
        newMenu: {
          name: "",
          freq: "",
        },
      }
    },
    mounted() {
      this.getMenuList()
    },
    methods: {
      getMenuList: function () {
        axios.get(`http://${window.location.host}/api/menu/${this.$route.params.id}/get`)
          .then(response => {
            this.menulist = response.data
            console.log(this.menulist);
          })
          .catch(e => {
              console.log(e);
          })
      },
      addMenu: function () {
        axios.post(`http://${window.location.host}/api/menu/${this.$route.params.id}/add`, {'data':this.newMenu})
          .then(response => {
            this.items = response.data
          })
          .catch(e => {
              console.log(e);
          })
      },
    }
};
</script>

<style scoped>
</style>
