<!-- src/views/MenuLoaderView.vue -->
<template>
  <v-container
    class="fill-height"
    fluid
  >
    <v-row
      align="center"
      justify="center"
    >
      <v-col cols="auto">
        <v-progress-circular
          indeterminate
          size="64"
          color="primary"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: "MenuLoaderView",
};
</script>

<style scoped>
.fill-height {
  height: 100vh;
}
</style>
