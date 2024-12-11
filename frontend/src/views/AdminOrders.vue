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
            {{ order.vendor_id }}
          </td>
          <td>
            <span
              class="badge"
              :class="{
                'bg-success': order.state_id === 'collect',
                'bg-warning': order.state_id === 'order',
                'bg-danger': order.state_id === 'closed'}"
            >
              {{ order.state_id }}
            </span>
          </td>
          <td>
            {{ order.user_id }}
          </td>
          <td>
            {{ order.date_of_order }}
          </td>
          <td>
            {{ order.order_fee }}
          </td>
          <td>
            <!-- <div
              class="btn"
              :class="['text-' + auth.getUserColor ]"
              title="Üzlet elérhetőség ki/be kapcsolása"
              @click="toggleActivation(vendor)"
            >
              <svg
                v-if="order.active"
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                fill="currentColor"
                class="bi bi-toggle-on"
                viewBox="0 0 16 16"
              >
                <path d="M5 3a5 5 0 0 0 0 10h6a5 5 0 0 0 0-10zm6 9a4 4 0 1 1 0-8 4 4 0 0 1 0 8" />
              </svg>
              <svg
                v-else
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                fill="currentColor"
                class="bi bi-toggle-off"
                viewBox="0 0 16 16"
              >
                <path d="M11 4a4 4 0 0 1 0 8H8a5 5 0 0 0 2-4 5 5 0 0 0-2-4zm-6 8a4 4 0 1 1 0-8 4 4 0 0 1 0 8M0 8a5 5 0 0 0 5 5h6a5 5 0 0 0 0-10H5a5 5 0 0 0-5 5" />
              </svg>
            </div>
            <div
              class="btn"
              :class="['text-' + auth.getUserColor ]"
              title="Üzlet beállítások"
              @click="openVendorConfiguration(vendor.id)"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                fill="currentColor"
                class="bi bi-gear-fill"
                viewBox="0 0 16 16"
              >
                <path d="M9.405 1.05c-.413-1.4-2.397-1.4-2.81 0l-.1.34a1.464 1.464 0 0 1-2.105.872l-.31-.17c-1.283-.698-2.686.705-1.987 1.987l.169.311c.446.82.023 1.841-.872 2.105l-.34.1c-1.4.413-1.4 2.397 0 2.81l.34.1a1.464 1.464 0 0 1 .872 2.105l-.17.31c-.698 1.283.705 2.686 1.987 1.987l.311-.169a1.464 1.464 0 0 1 2.105.872l.1.34c.413 1.4 2.397 1.4 2.81 0l.1-.34a1.464 1.464 0 0 1 2.105-.872l.31.17c1.283.698 2.686-.705 1.987-1.987l-.169-.311a1.464 1.464 0 0 1 .872-2.105l.34-.1c1.4-.413 1.4-2.397 0-2.81l-.34-.1a1.464 1.464 0 0 1-.872-2.105l.17-.31c.698-1.283-.705-2.686-1.987-1.987l-.311.169a1.464 1.464 0 0 1-2.105-.872zM8 10.93a2.929 2.929 0 1 1 0-5.86 2.929 2.929 0 0 1 0 5.858z" />
              </svg>
            </div> -->
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

export default {
    name: "AdminOrdesView",
    components: {
      Paginator
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
        totalCount: 0
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
    }
};
</script>

<style scoped>
</style>
