<template>
  <div
    class="row d-flex"
  >
    <div class="col-md-7 col-sm-12">
      <div class="row p-2">
        <MenuList
          key="0"
        />
        <GlobalBasket class="mt-2 d-md-none" />
      </div>
    </div>
    <div class="my-sticky-container col-12 col-md-5 order-first order-md-last">
      <div class="row p-2 ">
        <LocalBasket />
      </div>
      <div class="row p-2 d-none d-md-flex">
        <GlobalBasket />
      </div>
    </div>
  </div>

  <!-- <div
      v-else
      class="row col d-flex justify-content-center align-items-center"
    >
      <div
        class="spinner-border"
        style="width: 3rem; height: 3rem;"
      />
    </div> -->
</template>

<script>
import LocalBasket from '@/components/LocalBasket.vue';
import GlobalBasket from '@/components/GlobalBasket.vue';
import MenuList from '@/components/MenuList.vue';
// import { state } from "@/socket";

export default {
  name: 'MenuView',
  components: {
    LocalBasket,
    GlobalBasket,
    MenuList
  },
  data() {
    return {
    };
  },
};
</script>

<style scoped>
@media only screen and (max-width: 768px){
  .my-sticky-container {
        position: sticky;
        top: 5px;
        z-index: 1;
  }
 }
</style>
