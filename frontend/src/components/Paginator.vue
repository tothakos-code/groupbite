<template>
  <nav>
    <ul class="pagination">
      <!-- Previous Button -->
      <li
        class="page-item"
        :class="{ disabled: currentPage === 1 }"
      >
        <a
          class="page-link"
          :class="['text-' + auth.getUserColor, 'focus-ring focus-ring-' + auth.getUserColor]"
          href="#"
          aria-label="Previous"
          @click.prevent="changePage(currentPage - 1)"
        >
          <span aria-hidden="true">&laquo;</span>
        </a>
      </li>

      <!-- Show first page and ellipsis if necessary -->
      <li
        v-if="shouldShowStartEllipsis"
        class="page-item"
      >
        <a
          class="page-link"
          :class="['text-' + auth.getUserColor]"
          href="#"
          @click.prevent="changePage(1)"
        >
          1
        </a>
      </li>
      <li
        v-if="shouldShowStartEllipsis"
        class="page-item disabled"
      >
        <span class="page-link">...</span>
      </li>

      <!-- Dynamic Page Numbers -->
      <li
        v-for="page in pages"
        :key="page"
        class="page-item"
        :class="[{ active: page === currentPage }, 'text-' + auth.getUserColor ]"
      >
        <a
          class="page-link"
          href="#"
          :class="[(page === currentPage ? ' bg-' + auth.getUserColor+ ' border-' + auth.getUserColor : 'text-' + auth.getUserColor), 'focus-ring focus-ring-' + auth.getUserColor]"
          @click.prevent="changePage(page)"
        >
          {{ page }}
        </a>
      </li>

      <!-- Show last page and ellipsis if necessary -->
      <li
        v-if="shouldShowEndEllipsis"
        class="page-item disabled"
      >
        <span class="page-link">...</span>
      </li>
      <li
        v-if="shouldShowEndEllipsis"
        class="page-item"
      >
        <a
          class="page-link"
          :class="['text-' + auth.getUserColor, 'focus-ring focus-ring-' + auth.getUserColor]"
          href="#"
          @click.prevent="changePage(totalPages)"
        >
          {{ totalPages }}
        </a>
      </li>

      <!-- Next Button -->
      <li
        class="page-item"
        :class="{ disabled: currentPage === totalPages }"
      >
        <a
          class="page-link"
          :class="['text-' + auth.getUserColor, 'focus-ring focus-ring-' + auth.getUserColor]"
          href="#"
          aria-label="Next"
          @click.prevent="changePage(currentPage + 1)"
        >
          <span aria-hidden="true">&raquo;</span>
        </a>
      </li>
    </ul>
  </nav>
</template>

<script>
import { useAuth } from "@/stores/auth";
export default {
  name: "PaginationControl",
  props: {
    totalPages: {
      type: Number,
      required: true,
    },
    currentPage: {
      type: Number,
      required: true,
    },
    range: {
      type: Number,
      default: 10,
    },
  },
  emits: ["page-change"],
  setup() {
    const auth = useAuth();
    return {
      auth
    }
  },
  computed: {
    pages() {
      const pages = [];
      const halfRange = Math.floor(this.range / 2);
      let start = Math.max(1, this.currentPage - halfRange);
      let end = Math.min(this.totalPages, this.currentPage + halfRange);

      // Adjust start or end if at the beginning or end of pagination
      if (start === 1) {
        end = Math.min(this.range, this.totalPages);
      } else if (end === this.totalPages) {
        start = Math.max(1, this.totalPages - this.range + 1);
      }

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
      console.log(pages);
      return pages;
    },
    shouldShowStartEllipsis() {
      return this.pages[0] > 2;
    },
    shouldShowEndEllipsis() {
      return this.pages[this.pages.length - 1] < this.totalPages - 1;
    },
  },
  methods: {
    changePage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.$emit("page-change", page);
      }
    },
  },
};
</script>

<style scoped>
.page-item.disabled .page-link {
  pointer-events: none;
  color: #ccc;
}
.page-item.active .page-link {
  font-weight: bold;
  pointer-events: none;
  color: white;
}
</style>
