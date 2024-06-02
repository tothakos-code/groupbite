<template>
  <teleport to="body">
    <div
      ref="modal"
      class="modal fade"
      :class="{ show: active, 'd-block': active }"
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
            <button
              class="btn btn-secondary"
              @click="$emit('cancel')"
            >
              Mégse
            </button>
            <button
              class="btn"
              :class="['btn-' + auth.getUserColor ]"
              @click="$emit('confirm')"
            >
              Folytat
            </button>
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
import { ref, watch } from 'vue';
import { useAuth } from '@/stores/auth';

export default {
  name: 'BasePopup',
  props: {
    title: String(""),
    showModal: Boolean
  },
  emits: ['cancel', 'confirm'],
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
