<template>
  <div
    class="d-flex"
  >
    <div class=" rounded rounded-circle m-1">
      <a
        type="button"
        class="btn-outline-secondary text-secondary"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="40"
          height="40"
          fill="currentColor"
          class="bi bi-info-circle"
          viewBox="0 0 16 16"
        >
          <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16" />
          <path d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0" />
        </svg>
        <v-menu
          activator="parent"
        >
          <v-list min-width="200">
            <v-list-item
              target="_blank"
              class="text-decoration-none"
              href="https://docs.google.com/document/d/1x9Wvp5DPZun5OCcNV1B2limlL940EAX6gm03St_Hw-c/edit?usp=sharing"
            >

              <span>
                Felhasználói kézikönyv
              </span>


            </v-list-item>
            <v-list-item
              target="_blank"
              class="text-decoration-none"
              :href="'https://github.com/tothakos-code/groupbite/releases/tag/' + showVersion()"
            >
              <span>
                Verzió: {{ showVersion() }}
              </span>
            </v-list-item>
          </v-list>
        </v-menu>
      </a>
    </div>
  </div>
</template>

<script>

export default {
  name: "VersionInfo",
  methods:{
    showVersion: function() {
      // eslint-disable-next-line
      return process.env.VUE_APP_VERSION;
    },
  }
}
</script>

<style>
@media (max-width: 768px) {
     .rounded-sm {
       border-radius: 0.375rem !important;
     }
     .hide-sm-arrow::after {
      display: none !important;
    }
   }
</style>
