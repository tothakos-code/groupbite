<template>
  <Popup
    :show-modal="show"
    title="Profil beállítások"
    confirm-text="Mentés"
    @cancel="onCancel()"
    @confirm="updateUser()"
  >
    <p>A nevednek a könnyebb beazonosítás miatt egyedinek kell lennie. Használj egy becenevet amiről mindneki tudja, hogy te vagy az.</p>
    <p>A nevedet itt tudod megváltoztatni:</p>
    <div class="input-group mb-3">
      <span class="input-group-text">Név</span>
      <input
        v-model.trim="username"
        type="text"
        class="form-control"
        placeholder="Username"
        aria-label="Username"
        aria-describedby="basic-addon1"
      >
    </div>

    <hr>
    <h6 class="mt-3 mb-2">
      <v-icon
        size="small"
        color="warning"
      >
        mdi-star
      </v-icon>
      Kedvencek
    </h6>
    <div
      v-if="groupedFavourites.length === 0"
      class="text-medium-emphasis small"
    >
      Még nincs kedvenc. A menün a ★ ikonra kattintva adhatsz hozzá.
    </div>
    <div
      v-for="group in groupedFavourites"
      :key="group.vendorId"
      class="mb-3"
    >
      <div class="fw-bold small mb-1">
        {{ group.vendorName }}
      </div>
      <div
        v-for="fav in group.items"
        :key="fav.id"
        class="d-flex align-items-center justify-content-between mb-1"
      >
        <span class="small">{{ fav.item_name }}</span>
        <v-btn
          icon="mdi-close"
          size="x-small"
          variant="text"
          color="error"
          @click="removeFavourite(group.vendorId, fav.id)"
        />
      </div>
    </div>

    <!--
    <span class="input-group-radio">Felület szine:</span>
    <div class="d-flex justify-content-around m-2">
      <input
        id="falusi-outlined"
        v-model="ui_color"
        type="radio"
        class="btn-check"
        name="options-outlined"
        value="falusi"
        autocomplete="off"
        @change="onColorChange()"
      >
      <label
        class="btn btn-outline-falusi"
        for="falusi-outlined"
      >Alap</label>

      <input
        id="info-outlined"
        v-model="ui_color"
        type="radio"
        class="btn-check"
        name="options-outlined"
        value="steelblue"
        autocomplete="off"
        @change="onColorChange()"
      >
      <label
        class="btn btn-outline-steelblue"
        for="info-outlined"
      >Acélkék</label>

      <input
        id="danger-outlined"
        v-model="ui_color"
        type="radio"
        class="btn-check"
        name="options-outlined"
        value="raspberry"
        autocomplete="off"
        @change="onColorChange()"
      >
      <label
        class="btn btn-outline-raspberry"
        for="danger-outlined"
      >Málna</label>

      <input
        id="warning1-outlined"
        v-model="ui_color"
        type="radio"
        class="btn-check"
        name="options-outlined"
        value="tigragold"
        autocomplete="off"
        @change="onColorChange()"
      >
      <label
        class="btn btn-outline-tigragold"
        for="warning1-outlined"
      >Tigra</label>
    </div> -->
  </Popup>
</template>

<script>
import Popup from "./Popup.vue";
import { useAuth } from "@/stores/auth";
import { useFavouritesStore } from "@/stores/favourites";
import { useVendorStore } from "@/stores/vendor";

export default {
  name: "UserProfilePopup",
  components: {
    Popup
  },
  props: {
    show: Boolean
  },
  emits: ["cancel", "confirm"],
  setup() {
    const auth = useAuth();
    const favouritesStore = useFavouritesStore();
    const vendorStore = useVendorStore();
    return { auth, favouritesStore, vendorStore };
  },
  data() {
    return {
      username: this.auth.user.username,
      theme: "",
      ui_color: "",
      allFavourites: [],
    }
  },
  computed: {
    groupedFavourites() {
      const groups = {};
      for (const fav of this.allFavourites) {
        if (!groups[fav.vendor_id]) {
          const vendor = this.vendorStore.vendors.find(v => v.id === fav.vendor_id);
          groups[fav.vendor_id] = {
            vendorId: fav.vendor_id,
            vendorName: vendor?.name ?? fav.vendor_id,
            items: [],
          };
        }
        groups[fav.vendor_id].items.push(fav);
      }
      return Object.values(groups);
    },
  },
  watch: {
    show(val) {
      if (val) this.loadAllFavourites();
    },
  },
  mounted() {
    this.loadAllFavourites();
  },
  methods: {
    async loadAllFavourites() {
      this.allFavourites = await this.favouritesStore.fetchAllFavourites();
    },
    async removeFavourite(vendorId, favouriteId) {
      await this.favouritesStore.removeFavourite(vendorId, favouriteId);
      this.allFavourites = this.allFavourites.filter(f => f.id !== favouriteId);
    },
    updateUser: function() {
      let user_update_obj = {};
      user_update_obj.id = this.auth.user.id
      if (this.username !== this.auth.user.username) {
        user_update_obj.username = this.username
      }

      user_update_obj.ui_color = this.ui_color
      this.auth.update(user_update_obj)
        .then(response => {
        let user = response.data.data;
        if (response.data.error === undefined) {
          this.auth.$patch({
            user: user
          });
          this.$emit("cancel");
        }
      });
    },
    onCancel: function() {
      this.$emit("cancel")
    },
    onColorChange: function() {
      this.auth.user.ui_color = this.ui_color
    }
  }
}
</script>

<style>

</style>
