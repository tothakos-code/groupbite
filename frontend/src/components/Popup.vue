<template>
  <teleport to="body">
    <div
      ref="modal"
      class="modal fade modal-dialog-scrollable"
      :class="{ show: active, 'd-block': active, 'modal-lg': large }"
      tabindex="-1"
      role="dialog"
      :aria-hidden="active"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h2>{{ title }}</h2>
          </div>
          <div class="modal-body">
            <slot />
          </div>
          <div class="modal-footer">
            <v-btn
              v-if="cancelBtn === true"
              class="bg-background"
              @click="$emit('cancel')"
            >
              {{ cancelText }}
            </v-btn>
            <v-btn
              v-if="confirmBtn === true"
              class="bg-primary"
              @click="$emit('confirm')"
            >
              {{ confirmText }}
            </v-btn>
          </div>
        </div>
      </div>
    </div>
    <div
      class="fade"
      :class="{ show: active, 'modal-backdrop show': active }"
    />
  </teleport>
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

    watch(() => props.showModal, (newValue, oldValue) => {
      if (newValue !== oldValue) {
        active.value = props.showModal;
        const body = document.querySelector("body");
        props.showModal ? body.classList.add("modal-open") : body.classList.remove("modal-open");
      }
    },{immediate:true, deep: true});

    return {
      active,
      auth
    }
  }
}
</script>

<style>
</style>
