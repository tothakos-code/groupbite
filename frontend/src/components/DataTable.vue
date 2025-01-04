<template lang="html">
  <div class="">
    <div
      class="row mt-2"
    >
      <div class="col">
        <div class="row">
          <label for="itemName">
            Keresés:
          </label>
        </div>
        <div class="row">
          <div class="col-6">
            <input
              v-model.trim="searchString"
              type="text"
              name="itemName"
              class="form-control"
            >
          </div>
          <button
            class="btn btn-primary col-auto"
            type="button"
            name="save"
            @click="search()"
          >
            keresés
          </button>
        </div>
      </div>
    </div>
    <table class="table table-striped table-hover ">
      <thead>
        <tr class="">
          <th
            v-for="label in labelList"
            :key="label"
            scope="col"
            class="col-auto"
          >
            {{ label }}
          </th>
        </tr>
      </thead>
      <tbody
        v-if="!isLoading"
        class="table-group-divider"
      >
        <tr
          v-for="data in dataList"
          :key="data.id"
          class=""
        >
          <!-- <th
            scope="row"
            class="col-auto"
          >
            {{ data.id }}
          </th> -->
          <td
            v-for="(value, key) in limitedColumns(data)"
            :key="key"
            class="col-auto"
          >
            <span>
              {{ value }}
            </span>
          </td>
          <td class="col-auto">
            <input
              id="flexCheckDefault"
              v-model="selectedDatas"
              class="form-check-input"
              name="flexRadioDefault"
              :type="multiSelect ? 'checkbox' : 'radio'"

              :value="data"
            >
          </td>
        </tr>
      </tbody>
      <div
        v-else
        class="row text-center"
      >
        <div
          class="spinner-border"
          role="status"
        >
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
    </table>
    <Paginator
      :total-pages="Math.ceil(totalCount/limit)"
      :current-page="currentPage"
      :range="5"
      @page-change="handlePageChange"
    />
  </div>
</template>

<script>
import { useAuth } from "@/stores/auth";
import Paginator from "./Paginator.vue";

export default {
  name: "DataTable",
  components: {
    Paginator
  },
  props: {
    labelList: {
      type: Array,
      default: () => []
    },
    limitCols: {
      type: Array,
      default: () => []
    },
    getterFunc: {
      type: Function,
      default: () => []
    },
    multiSelect: {
      type: Boolean,
      default: false
    },
  },
  emits: ["search", "select", "cancel"],
  setup() {
      const auth = useAuth();
      return {
        auth
      }
  },
  data() {
    return {
      dataList: [],
      isLoading: false,
      searchString: "",
      limit: 10,
      currentPage: 1,
      totalCount: 0,
      selectedDatas: []
    }
  },
  mounted() {
    this.callGetter()
  },
  methods: {
    limitedColumns(columns) {
      let result = {};
      if (this.limitCols.length === 0) {
        return columns
      }
      for (const [key, value] of Object.entries(columns)) {
        if (this.limitCols.includes(key)) {
          result[key] = value
        }
      }
      return result
    },
    search() {
      this.callGetter()
    },
    handlePageChange(page) {
      this.currentPage = page;
      this.callGetter()
    },
    callGetter() {
      this.getterFunc(this.$route.params.id, {
          "search": this.searchString,
          "limit": this.limit,
          "page": this.currentPage
        }).then(response => {
          this.currentPage = response.data.data.page;
          this.limit = response.data.data.limit;
          this.totalCount = response.data.data.total_count;
          this.dataList = response.data.data.menus;
          this.isLoading = false;
        })
        .catch(e => {
            console.log(e);
        })
    }
  }
}
</script>

<style lang="css" scoped>
</style>
