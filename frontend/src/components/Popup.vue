<template>
  <v-dialog
    v-model="active"
    :max-width="large ? '800px' : '500px'"
    persistent
  >
    <v-card>
      <v-card-title class="text-h5 pa-4">
        {{ title }}
      </v-card-title>

      <v-card-text class="pa-4">
        <slot />
      </v-card-text>

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn
          v-if="cancelBtn"
          variant="text"
          @click="$emit('cancel')"
        >
          {{ cancelText }}
        </v-btn>
        <v-btn
          v-if="confirmBtn"
          variant="elevated"
          color="primary"
          @click="$emit('confirm')"
        >
          {{ confirmText }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { ref, watch } from "vue";
import { useAuth } from "@/stores/auth";

export default {
  name: "BasePopup",
  props: {
    title: {
      type: String,
      default: ""
    },
    showModal: Boolean,
    cancelText: {
      type: String,
      default: "Mégse"
    },
    confirmText: {
      type: String,
      default: "Folytat"
    },
    cancelBtn: {
      type: Boolean,
      default: true
    },
    confirmBtn: {
      type: Boolean,
      default: true
    },
    large: {
      type: Boolean,
      default: false
    },
  },
  emits: ["cancel", "confirm"],
  setup(props) {
    const auth = useAuth();
    const active = ref(props.showModal);

    watch(() => props.showModal, (newValue) => {
      active.value = newValue;
    }, { immediate: true });

    return {
      active,
      auth
    }
  }
}
</script>
