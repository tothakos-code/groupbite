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
            <slot></slot>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="$emit('cancel')">Mégse</button>
            <button class="btn" :class="['btn-' + this.userColor ]" @click="$emit('confirm')">Folytat</button>
          </div>
        </div>
      </div>
    </div>
    <div class="fade" :class="{ show: active, 'modal-backdrop show': active }"></div>
  </teleport>
</template>

<script>
import { ref, watch} from 'vue';
import { state } from '@/socket';
export default {
  name: 'PopupBase',
  props: {
    title: String,
    showModal: Boolean
  },
  emits: ['cancel', 'confirm'],
  setup(props) {
    const active = ref(props.showModal);

    watch(() => props.showModal, (newValue, oldValue) => {
      if (newValue !== oldValue) {
        active.value = props.showModal;
        const body = document.querySelector("body");
        props.showModal ? body.classList.add("modal-open") : body.classList.remove("modal-open");
      }
    },{immediate:true, deep: true});

    return {
      active
    }
  },
  computed: {
    userColor() {
      return state.user.ui_color ? state.user.ui_color : "falusi";
    }
  }
}
</script>

<style>
</style>
