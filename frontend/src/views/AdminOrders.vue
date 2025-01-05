<template>
  <div class="row ms-2 mt-2">
    <h1 class="col d-flex justify-content-start">
      Rendelések
    </h1>
  </div>
  <div
    v-if="!isLoading"
    class="row ms-2"
  >
    <table class="table table-striped table-hover">
      <thead>
        <tr>
          <th scope="col">
            #
          </th>
          <th scope="col">
            Üzelt
          </th>
          <th scope="col">
            Állapot
          </th>
          <th scope="col">
            Felhasználó
          </th>
          <th scope="col">
            Dátum
          </th>
          <th scope="col">
            Rendelési díj
          </th>
          <th scope="col">
            Műveletek
          </th>
        </tr>
      </thead>
      <tbody class="table-group-divider">
        <tr
          v-for="order in orders"
          :key="order.id"
        >
          <th scope="row">
            {{ order.id }}
          </th>
          <td>
            {{ order.vendor }}
          </td>
          <td>
            <v-select
              v-if="editing && order.id === editing"
              v-model="order.state_id"
              :items="orderStates"
            >
              <template #selection="{ item }">
                <v-chip
                  :class="item.value === 'collect' ? 'bg-success' :
                    item.title === 'order' ? 'bg-warning' :
                    item.title === 'closed' ? 'bg-error' : ''"
                  border="sm"
                  flat
                >
                  <span>{{ item.title }}</span>
                </v-chip>
              </template>
              <template #item="{ props, item }">
                <v-list-item
                  v-bind="props"
                  title=""
                >
                  <v-chip

                    :class="item.value === 'collect' ? 'bg-success' :
                      item.title === 'order' ? 'bg-warning' :
                      item.title === 'closed' ? 'bg-error' : ''"
                    border="sm"
                    flat
                  >
                    <span>{{ item.title }}</span>
                  </v-chip>
                </v-list-item>
              </template>
            </v-select>
            <v-chip
              v-else
              :class="order.state_id === 'collect' ? 'bg-success' :
                order.state_id === 'order' ? 'bg-warning' :
                order.state_id === 'closed' ? 'bg-error' : ''"
              border="sm"
              flat
            >
              <span>{{ order.state_id }}</span>
            </v-chip>
          </td>
          <td>
            {{ order.user_id }}
          </td>
          <td>
            {{ order.date_of_order }}
          </td>
          <td>
            <VNumberInput
              v-if="editing && order.id === editing"
              v-model="order.order_fee"
              :step="50"
              control-variant="split"
            />
            <span v-else>{{ order.order_fee }}</span>
          </td>
          <td>
            <div
              v-if="order.id != editing"
              class="col-auto"
            >
              <v-btn
                type="button"
                name="button"
                title="Szerkesztés"
                class="bg-primary me-1 mt-1"
                icon
                size="small"
                border="primary thin"
                rounded
                varian="text"
                @click="edit(order.id)"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  fill="currentColor"
                  class="bi bi-pen"
                  viewBox="0 0 16 16"
                >
                  <path d="m13.498.795.149-.149a1.207 1.207 0 1 1 1.707 1.708l-.149.148a1.5 1.5 0 0 1-.059 2.059L4.854 14.854a.5.5 0 0 1-.233.131l-4 1a.5.5 0 0 1-.606-.606l1-4a.5.5 0 0 1 .131-.232l9.642-9.642a.5.5 0 0 0-.642.056L6.854 4.854a.5.5 0 1 1-.708-.708L9.44.854A1.5 1.5 0 0 1 11.5.796a1.5 1.5 0 0 1 1.998-.001m-.644.766a.5.5 0 0 0-.707 0L1.95 11.756l-.764 3.057 3.057-.764L14.44 3.854a.5.5 0 0 0 0-.708z" />
                </svg>
              </v-btn>
            </div>
            <div
              v-if="editing && order.id === editing"
              class="col-auto"
            >
              <v-btn
                type="button"
                name="button"
                title="Mentés"
                class="bg-primary me-1 mt-1"
                icon
                size="small"
                border="primary thin"
                rounded
                varian="text"
                @click="updateOrder(order)"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  fill="currentColor"
                  class="bi bi-floppy"
                  viewBox="0 0 16 16"
                >
                  <path d="M11 2H9v3h2z" />
                  <path d="M1.5 0h11.586a1.5 1.5 0 0 1 1.06.44l1.415 1.414A1.5 1.5 0 0 1 16 2.914V14.5a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 0 14.5v-13A1.5 1.5 0 0 1 1.5 0M1 1.5v13a.5.5 0 0 0 .5.5H2v-4.5A1.5 1.5 0 0 1 3.5 9h9a1.5 1.5 0 0 1 1.5 1.5V15h.5a.5.5 0 0 0 .5-.5V2.914a.5.5 0 0 0-.146-.353l-1.415-1.415A.5.5 0 0 0 13.086 1H13v4.5A1.5 1.5 0 0 1 11.5 7h-7A1.5 1.5 0 0 1 3 5.5V1H1.5a.5.5 0 0 0-.5.5m3 4a.5.5 0 0 0 .5.5h7a.5.5 0 0 0 .5-.5V1H4zM3 15h10v-4.5a.5.5 0 0 0-.5-.5h-9a.5.5 0 0 0-.5.5z" />
                </svg>
              </v-btn>
            </div>
            <div
              v-if="editing && order.id === editing"
              class="col-auto"
            >
              <v-btn
                type="button"
                name="button"
                title="Mégse"
                class="bg-primary me-1 mt-1"
                icon
                size="small"
                border="primary thin"
                rounded
                varian="text"
                @click="cancelEdit()"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  fill="currentColor"
                  class="bi bi-x"
                  viewBox="0 0 16 16"
                >
                  <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708" />
                </svg>
              </v-btn>
            </div>
          </td>
        </tr>
      </tbody>
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
import { useOrderStore } from "@/stores/order";
import Paginator from "@/components/Paginator.vue";
import { VNumberInput } from 'vuetify/labs/VNumberInput'

export default {
    name: "AdminOrdesView",
    components: {
      Paginator,
      VNumberInput
    },
    setup() {
      const auth = useAuth();
      const orderStore = useOrderStore();
      return {
        auth,
        orderStore
      }
    },
    data() {
      return {
        orders: [],
        isLoading: true,
        limit: 10,
        currentPage: 1,
        totalCount: 0,
        editing: false,
        editOriginal: null,
        orderStates: ["collect","order","closed",]
      }
    },
    mounted() {
      this.refreshOrdersList()
    },
    methods: {
      handlePageChange(page) {
        this.currentPage = page;
        this.refreshOrdersList()
      },
      refreshOrdersList: function () {
        this.orderStore.fetchAll({
            "limit": this.limit,
            "page": this.currentPage
          })
          .then(response => {
            if (response.status === 200) {
              this.orders = response.data.data.items;
              this.currentPage = response.data.data.page;
              this.limit = response.data.data.limit;
              this.totalCount = response.data.data.total_count;
            }
            this.isLoading = false;
          })
      },
      edit(order_id) {
        this.editing = order_id
      },
      cancelEdit() {
        this.editing = false;
        this.refreshOrdersList()
      },
      updateOrder(order){
        this.orderStore.update(order.id, {
          "state_id": order.state_id,
          "order_fee": order.order_fee
        } )
          .then(response => {
            if (response.status === 200) {
              this.editing = false;
              this.refreshOrdersList()
            }
          })
      }
    }
};
</script>

<style scoped>
</style>
