<template>
  <div class="row ms-2">
    <div class="">
      <div
        class=""
      >
        <label for="itemName">
          Menü:
          <select
            v-model="selectedMenu"
            name="itemMenu"
          >
            <option
              v-for="m in menus"
              :key="m.id"
              :value="m.id"
            >{{ m.name }} - {{ m.date }}</option>
          </select>
        </label>
        <label for="itemName">
          Név:
          <input
            v-model="item.name"
            type="text"
            name="itemName"
          >
        </label>
        <label for="itemSize">
          Méret:
          <input
            v-model="item.size"
            type="text"
            name="itemSize"
          >
        </label>
        <label for="itemPrice">
          Ár:
          <input
            v-model="item.price"
            type="number"
            name="itemPrice"
          >
        </label>
      </div>
      <button
        class="btn"
        :class="['btn-' + auth.userColor.value ]"
        type="button"
        name="save"
        @click="addToMenu()"
      >
        Menühöz adás
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
          v-for="item,index in items"
          :key="index"
        >
          <th scope="row">
            {{ item.id }}
          </th>
          <td>
            {{ item.name }}
          </td>
          <td>
            {{ item.size }}
          </td>
          <td>
            {{ item.price }}
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
        menus: [],
        selectedMenu: "",
        item: {
          name: "",
          size: "",
          price: 0,
        },
        items: []
      }
    },
    watch: {
      selectedMenu() {
        this.getItemList()
      }
    },
    mounted() {
      this.getMenuList()
    },
    methods: {
      getMenuList: function () {
        axios.get(`http://${window.location.host}/api/menu/${this.$route.params.id}/get`)
          .then(response => {
            console.log(response);
            this.menus = response.data
          })
          .catch(e => {
              console.log(e);
          })
      },
      getItemList: function () {
        axios.get(`http://${window.location.host}/api/menu/${this.$route.params.id}/get-items/${this.selectedMenu}`)
          .then(response => {
            console.log(response);
            this.items = response.data
          })
          .catch(e => {
              console.log(e);
          })
      },
      addToMenu: function () {
        axios.post(`http://${window.location.host}/api/menu/${this.$route.params.id}/item-add`, {'data':this.item, 'menu': this.selectedMenu})
          .then(() => {
            this.getMenuList()
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
