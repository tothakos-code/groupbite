<template>
  <div class="">
    <div
      class=""
    >
      <div class="row ms-2">
        <div
          class="row my-2"
        >
          <div
            class="row mt-2"
          >
            <span class="row ms-1 h4">
              Új étel hozzáadása:
            </span>
            <div class="col-2">
              <label for="itemName">
                Név:
              </label>
              <input
                v-model="newItem.name"
                type="text"
                name="itemName"
                class="form-control"
              >
            </div>

            <div class="col-2">
              <label for="itemDesc">
                Leírás:
              </label>
              <input
                v-model="newItem.description"
                type="text"
                name="itemDesc"
                class="form-control"
              >
            </div>
            <div class="col-2">
              <label for="itemCategory">
                Kategória:
              </label>
              <input
                v-model="newItem.category"
                type="text"
                name="itemCategory"
                class="form-control"
              >
            </div>
            <v-btn
              class="bg-primary col-auto align-self-end"
              type="button"
              name="save"
              @click="addToMenu()"
            >
              Menühöz adás
            </v-btn>
          </div>
          <div
            class="row mt-2"
          >
            <div class="col-2">
              <label for="itemName">
                Keresés:
              </label>
              <input
                v-model.trim="searchString"
                type="text"
                name="itemName"
                class="form-control"
              >
            </div>
            <v-btn
              class="bg-primary col-auto align-self-end"
              type="button"
              name="save"
              @click="search()"
            >
              keresés
            </v-btn>
          </div>
        </div>
      </div>
      <div class="mt-2">
        <table class="table table-striped table-bordered table-hover">
          <thead>
            <tr>
              <th
                scope="col"
                class="col-auto"
              >
                #
              </th>
              <th
                scope="col"
                class="col-auto"
              >
                Név
              </th>
              <th
                scope="col"
                class="col-auto"
              >
                Leírás
              </th>
              <th
                scope="col"
                class="col-auto"
              >
                Kategória
              </th>
              <th
                scope="col"
                class="col-auto"
              >
                Sorrend index
              </th>
              <th
                scope="col"
                class="col-auto"
              >
                Műveletek
              </th>
            </tr>
          </thead>
          <tbody
            v-if="!isLoading"
            class="table-group-divider"
          >
            <template
              v-for="[id, menuItem] in items"
              :key="id"
            >
              <tr>
                <td
                  scope="row"
                  class="col-auto"
                >
                  {{ menuItem.id }}
                </td>
                <td>
                  <input
                    v-if="menuItem.isEditing"
                    v-model="menuItem.name"
                    class="form-control"
                    type="text"
                  >
                  <span v-else>
                    {{ menuItem.name }}
                  </span>
                </td>
                <td>
                  <input
                    v-if="menuItem.isEditing"
                    v-model="menuItem.description"
                    class="form-control"
                    type="text"
                  >
                  <span v-else>
                    {{ menuItem.description }}
                  </span>
                </td>
                <td>
                  <input
                    v-if="menuItem.isEditing"
                    v-model="menuItem.category"
                    class="form-control"

                    type="text"
                  >
                  <span v-else>
                    {{ menuItem.category }}
                  </span>
                </td>
                <td>
                  <input
                    v-if="menuItem.isEditing"
                    v-model="menuItem.index"
                    class="form-control"
                    type="number"
                  >
                  <span v-else>
                    {{ menuItem.index }}
                  </span>
                </td>
                <td>
                  <v-btn
                    v-if="!menuItem.isEditing"
                    type="button"
                    name="button"
                    class="bg-primary me-1 mt-1"
                    icon
                    size="small"
                    border="primary thin"
                    varian="text"
                    rounded
                    title="Szerkesztés"
                    @click="edit(menuItem.id)"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="16"
                      height="16"
                      fill="currentColor"
                      class="bi bi-pen"
                      viewBox="0 0 16 16"
                    >
                      <path d="m13.498.795.149-.149a1.207 1.207 0 1 1 1.707 1.708l-.149.148a1.5 1.5 0 0 1-.059 2.059L4.854 14.854a.5.5 0 0 1-.233.131l-4 1a.5.5 0 0 1-.606-.606l1-4a.5.5 0 0 1 .131-.232l9.642-9.642a.5.5 0 0 0-.642.056L6.854 4.854a.5.5 0 1 1-.708-.708L9.44.854A1.5 1.5 0 0 1 11.5.796a1.5 1.5 0 0 1 1.998-.001m-.644.766a.5.5 0 0 0-.707 0L1.95 11.756l-.764 3.057 3.057-.764L14.44 3.854a.5.5 0 0 0 0-.708z" />
                    </svg>
                  </v-btn>
                  <div v-else>
                    <v-btn
                      type="button"
                      name="button"
                      class="bg-primary me-1 mt-1"
                      icon
                      size="small"
                      border="primary thin"
                      rounded
                      varian="text"
                      title="Mentés"
                      @click="updateItem(menuItem.id)"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="16"
                        height="16"
                        fill="currentColor"
                        class="bi bi-floppy"
                        viewBox="0 0 16 16"
                      >
                        <path d="M11 2H9v3h2z" />
                        <path d="M1.5 0h11.586a1.5 1.5 0 0 1 1.06.44l1.415 1.414A1.5 1.5 0 0 1 16 2.914V14.5a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 0 14.5v-13A1.5 1.5 0 0 1 1.5 0M1 1.5v13a.5.5 0 0 0 .5.5H2v-4.5A1.5 1.5 0 0 1 3.5 9h9a1.5 1.5 0 0 1 1.5 1.5V15h.5a.5.5 0 0 0 .5-.5V2.914a.5.5 0 0 0-.146-.353l-1.415-1.415A.5.5 0 0 0 13.086 1H13v4.5A1.5 1.5 0 0 1 11.5 7h-7A1.5 1.5 0 0 1 3 5.5V1H1.5a.5.5 0 0 0-.5.5m3 4a.5.5 0 0 0 .5.5h7a.5.5 0 0 0 .5-.5V1H4zM3 15h10v-4.5a.5.5 0 0 0-.5-.5h-9a.5.5 0 0 0-.5.5z" />
                      </svg>
                    </v-btn>
                    <v-btn
                      type="button"
                      name="button"
                      title="Mégse"
                      class="bg-primary me-1 mt-1"
                      icon
                      size="small"
                      border="primary thin"
                      rounded
                      varian="text"
                      @click="cancelEdit(menuItem.id)"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="16"
                        height="16"
                        fill="currentColor"
                        class="bi bi-x"
                        viewBox="0 0 16 16"
                      >
                        <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708" />
                      </svg>
                    </v-btn>
                  </div>
                  <v-btn
                    type="button"
                    name="button"
                    title="Törlés"
                    class="bg-primary me-1 mt-1"
                    icon
                    size="small"
                    border="primary thin"
                    rounded
                    varian="text"
                    @click="newSize(menuItem.id)"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="20"
                      height="20"
                      fill="currentColor"
                      class="bi bi-file-plus"
                      viewBox="0 0 16 16"
                    >
                      <path d="M8.5 6a.5.5 0 0 0-1 0v1.5H6a.5.5 0 0 0 0 1h1.5V10a.5.5 0 0 0 1 0V8.5H10a.5.5 0 0 0 0-1H8.5z" />
                      <path d="M2 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2zm10-1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1" />
                    </svg>
                  </v-btn>
                  <v-btn
                    type="button"
                    name="button"
                    title="Áthelyezés"
                    class="bg-primary me-1 mt-1"
                    icon
                    size="small"
                    border="primary thin"
                    rounded
                    varian="text"
                    @click="showMovePopup = true; selectedItem = menuItem"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="20"
                      height="20"
                      fill="currentColor"
                      class="bi bi-box-arrow-in-right"
                      viewBox="0 0 16 16"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M6 3.5a.5.5 0 0 1 .5-.5h8a.5.5 0 0 1 .5.5v9a.5.5 0 0 1-.5.5h-8a.5.5 0 0 1-.5-.5v-2a.5.5 0 0 0-1 0v2A1.5 1.5 0 0 0 6.5 14h8a1.5 1.5 0 0 0 1.5-1.5v-9A1.5 1.5 0 0 0 14.5 2h-8A1.5 1.5 0 0 0 5 3.5v2a.5.5 0 0 0 1 0z"
                      />
                      <path
                        fill-rule="evenodd"
                        d="M11.854 8.354a.5.5 0 0 0 0-.708l-3-3a.5.5 0 1 0-.708.708L10.293 7.5H1.5a.5.5 0 0 0 0 1h8.793l-2.147 2.146a.5.5 0 0 0 .708.708z"
                      />
                    </svg>
                  </v-btn>
                  <v-btn
                    type="button"
                    name="button"
                    title="Másolás"
                    class="bg-primary me-1 mt-1"
                    icon
                    size="small"
                    border="primary thin"
                    rounded
                    varian="text"
                    @click="showCopyPopup = true; selectedItem = menuItem"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="16"
                      height="16"
                      fill="currentColor"
                      class="bi bi-copy"
                      viewBox="0 0 16 16"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M4 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2zm2-1a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1zM2 5a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1v-1h1v1a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h1v1z"
                      />
                    </svg>
                  </v-btn>
                  <v-btn
                    type="button"
                    name="button"
                    title="Törlés"
                    class="bg-primary me-1 mt-1"
                    icon
                    size="small"
                    border="primary thin"
                    rounded
                    varian="text"
                    @click="deleteItem(menuItem.id)"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="16"
                      height="16"
                      fill="currentColor"
                      class="bi bi-trash"
                      viewBox="0 0 16 16"
                    >
                      <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z" />
                      <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z" />
                    </svg>
                  </v-btn>
                </td>
              </tr>
              <tr>
                <td />
                <td colSpan="4">
                  <table class="table mb-0 table-striped table-hover">
                    <thead>
                      <tr>
                        <th
                          scope="col"
                          class="col-auto"
                        >
                          Méret
                        </th>
                        <th
                          scope="col"
                          class="col-auto"
                        >
                          Ár
                        </th>
                        <th
                          scope="col"
                          class="col-auto"
                        >
                          Végtelen
                        </th>
                        <th
                          scope="col"
                          class="col-auto"
                        >
                          Mennyiség
                        </th>
                        <th
                          scope="col"
                          class="col-auto"
                        >
                          Sorrend index
                        </th>
                        <th
                          scope="col"
                          class="col-auto"
                        >
                          Műveletek
                        </th>
                      </tr>
                      <tr
                        v-for="[sizeId, size] in menuItem.sizes"
                        :key="'size-' + sizeId"
                      >
                        <td>
                          <input
                            v-if="size.isEditing"
                            v-model="size.name"
                            class="form-control"

                            type="text"
                          >
                          <span v-else>
                            {{ size.name }}
                          </span>
                        </td>
                        <td>
                          <input
                            v-if="size.isEditing"
                            v-model="size.price"
                            class="form-control"
                            type="number"
                          >
                          <span v-else>
                            {{ size.price }}
                          </span>
                        </td>
                        <td>
                          <v-checkbox-btn
                            v-model="size.unlimited"
                            :readonly="!size.isEditing"
                          />
                        </td>
                        <td>
                          <input
                            v-if="size.isEditing"
                            v-model="size.quantity"
                            class="form-control"
                            title="negatív érték ∞-t jelent"
                            type="number"
                          >
                          <span v-else-if="!size.unlimited">
                            {{ size.quantity }}
                          </span>
                          <span v-else>
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              width="16"
                              height="16"
                              fill="currentColor"
                              class="bi bi-infinity"
                              viewBox="0 0 16 16"
                            >
                              <path d="M5.68 5.792 7.345 7.75 5.681 9.708a2.75 2.75 0 1 1 0-3.916ZM8 6.978 6.416 5.113l-.014-.015a3.75 3.75 0 1 0 0 5.304l.014-.015L8 8.522l1.584 1.865.014.015a3.75 3.75 0 1 0 0-5.304l-.014.015zm.656.772 1.663-1.958a2.75 2.75 0 1 1 0 3.916z" />
                            </svg>
                          </span>
                        </td>

                        <td>
                          <input
                            v-if="size.isEditing"
                            v-model="size.index"
                            class="form-control"
                            type="number"
                          >
                          <span v-else>
                            {{ size.index }}
                          </span>
                        </td>
                        <td>
                          <v-btn
                            v-if="!size.isEditing"
                            type="button"
                            name="button"
                            title="Szerkesztés"
                            class="bg-primary me-1 mt-1"
                            icon
                            size="small"
                            border="primary thin"
                            rounded
                            varian="text"
                            @click="editSize(menuItem.id, size.id)"
                          >
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              width="16"
                              height="16"
                              fill="currentColor"
                              class="bi bi-pen"
                              viewBox="0 0 16 16"
                            >
                              <path d="m13.498.795.149-.149a1.207 1.207 0 1 1 1.707 1.708l-.149.148a1.5 1.5 0 0 1-.059 2.059L4.854 14.854a.5.5 0 0 1-.233.131l-4 1a.5.5 0 0 1-.606-.606l1-4a.5.5 0 0 1 .131-.232l9.642-9.642a.5.5 0 0 0-.642.056L6.854 4.854a.5.5 0 1 1-.708-.708L9.44.854A1.5 1.5 0 0 1 11.5.796a1.5 1.5 0 0 1 1.998-.001m-.644.766a.5.5 0 0 0-.707 0L1.95 11.756l-.764 3.057 3.057-.764L14.44 3.854a.5.5 0 0 0 0-.708z" />
                            </svg>
                          </v-btn>
                          <div v-else>
                            <v-btn
                              type="button"
                              name="button"
                              title="Mentés"
                              class="bg-primary me-1 mt-1"
                              icon
                              size="small"
                              border="primary thin"
                              rounded
                              varian="text"
                              @click="updateSize(menuItem.id, size.id)"
                            >
                              <svg
                                xmlns="http://www.w3.org/2000/svg"
                                width="16"
                                height="16"
                                fill="currentColor"
                                class="bi bi-floppy"
                                viewBox="0 0 16 16"
                              >
                                <path d="M11 2H9v3h2z" />
                                <path d="M1.5 0h11.586a1.5 1.5 0 0 1 1.06.44l1.415 1.414A1.5 1.5 0 0 1 16 2.914V14.5a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 0 14.5v-13A1.5 1.5 0 0 1 1.5 0M1 1.5v13a.5.5 0 0 0 .5.5H2v-4.5A1.5 1.5 0 0 1 3.5 9h9a1.5 1.5 0 0 1 1.5 1.5V15h.5a.5.5 0 0 0 .5-.5V2.914a.5.5 0 0 0-.146-.353l-1.415-1.415A.5.5 0 0 0 13.086 1H13v4.5A1.5 1.5 0 0 1 11.5 7h-7A1.5 1.5 0 0 1 3 5.5V1H1.5a.5.5 0 0 0-.5.5m3 4a.5.5 0 0 0 .5.5h7a.5.5 0 0 0 .5-.5V1H4zM3 15h10v-4.5a.5.5 0 0 0-.5-.5h-9a.5.5 0 0 0-.5.5z" />
                              </svg>
                            </v-btn>
                            <v-btn
                              type="button"
                              name="button"
                              title="Mégse"
                              class="bg-primary me-1"
                              icon
                              size="small"
                              border="primary thin"
                              rounded
                              varian="text"
                              @click="cancelSizeEdit(menuItem.id, size.id)"
                            >
                              <svg
                                xmlns="http://www.w3.org/2000/svg"
                                width="16"
                                height="16"
                                fill="currentColor"
                                class="bi bi-x"
                                viewBox="0 0 16 16"
                              >
                                <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708" />
                              </svg>
                            </v-btn>
                          </div>
                          <v-btn
                            type="button"
                            name="button"
                            title="Törlés"
                            class="bg-primary me-1 mt-1"
                            icon
                            size="small"
                            border="primary thin"
                            rounded
                            varian="text"
                            @click="deleteSize(menuItem.id, size.id)"
                          >
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              width="16"
                              height="16"
                              fill="currentColor"
                              class="bi bi-trash"
                              viewBox="0 0 16 16"
                            >
                              <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z" />
                              <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z" />
                            </svg>
                          </v-btn>
                        </td>
                      </tr>
                    </thead>
                  </table>
                </td>
              </tr>
            </template>
          </tbody>
          <div
            v-else
            class="row text-center"
          >
            <div
              class="spinner-border"
              role="status"
            >
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
        </table>
        <Paginator
          :total-pages="Math.ceil(totalCount/limit)"
          :current-page="currentPage"
          :range="5"
          @page-change="handlePageChange"
        />
      </div>
    </div>
    <Popup
      title="Item áthelyezése"
      :show-modal="showMovePopup"
      confirm-text="Ok"
      :large="true"
      @cancel="showMovePopup=false"
      @confirm="moveItem()"
    >
      <DataTable
        ref="selectedMove"
        :getter-func="vendorStore.fetchMenus"
        :limit-cols="['id', 'date', 'name', 'freq']"
        :label-list="['date', 'freq', 'id', 'name']"
      />
    </Popup>
    <Popup
      title="Item másolása"
      :show-modal="showCopyPopup"
      confirm-text="Ok"
      :large="true"
      @cancel="showCopyPopup=false"
      @confirm="copyItem()"
    >
      <DataTable
        ref="selectedCopy"
        :getter-func="vendorStore.fetchMenus"
        :limit-cols="['id', 'date', 'name', 'freq']"
        :label-list="['date', 'freq', 'id', 'name']"
      />
    </Popup>
  </div>
</template>

<script>
import { useAuth } from "@/stores/auth";
import { useMenuStore } from "@/stores/menu";
import { useItemStore } from "@/stores/item";
import { useSizeStore } from "@/stores/size";
import { useVendorStore } from "@/stores/vendor";
import Paginator from "@/components/Paginator.vue";
import DataTable from "@/components/DataTable.vue";
import Popup from "@/components/Popup.vue";

export default {
    name: "VendorItemManager",
    components: {
      Paginator,
      Popup,
      DataTable
    },
    setup() {
      const auth = useAuth();
      const menuStore = useMenuStore();
      const itemStore = useItemStore();
      const sizeStore = useSizeStore();
      const vendorStore = useVendorStore();
      return {
        auth,
        menuStore,
        itemStore,
        sizeStore,
        vendorStore
      }
    },
    data() {
      return {
        newItem: {
          name: "",
          description: "",
          category: "",
          // price: 0,
          // quantity: -1,
          // unlimited: true,
          index: 0,
        },
        items: [],
        searchString: "",
        isLoading: true,
        showCopyPopup: false,
        showMovePopup: false,
        selectedItem: null,
        limit: 10,
        currentPage: 1,
        totalCount: 0
      }
    },
    mounted() {
      this.getItemList()
    },
    methods: {
      handlePageChange(page) {
        this.currentPage = page;
        this.getItemList()
      },
      getItemList() {
        this.menuStore.fetch(this.$route.params.menuId,{
            "search": this.searchString,
            "limit": this.limit,
            "page": this.currentPage
          }).then(
          response => {
            if (response.status === 200) {
              let menuItemsMap = new Map();
              response.data.data.items.forEach(item => {
                item.isEditing = false;


                let sizesMap = new Map();
                item.sizes.forEach(size => {
                  size.isEditing = false;
                  sizesMap.set(size.id, size);
                });
                item.sizes = sizesMap;
                menuItemsMap.set(item.id, item);
              });
              this.currentPage = response.data.data.page;
              this.limit = response.data.data.limit;
              this.totalCount = response.data.data.total_count;
              this.items = menuItemsMap;
              this.isLoading = false;
            }
          })
      },
      addToMenu: function () {
        this.newItem.menu_id = this.$route.params.menuId
        this.itemStore.add(this.newItem)
          .then(response => {
            if (response.status === 201) {
              this.getItemList()
              // this.newSize(response.data.data.id)
            }
          })
      },
      moveItem: function () {
        const item = this.selectedItem
        delete item["isEditing"]
        delete item["sizes"]
        item.menu_id = this.$refs.selectedMove.selectedDatas.id
        this.itemStore.update(item.id, item)
          .then(response => {
            if (response.status === 200) {
              this.showMovePopup=false
              this.getItemList()
            }
          })
      },
      copyItem: function () {
        const item = this.selectedItem
        delete item["isEditing"]
        const sizes = this.selectedItem.sizes
        delete item["sizes"]
        delete item["id"]
        item.menu_id = this.$refs.selectedCopy.selectedDatas.id
        this.itemStore.add(item)
          .then(response => {
            if (response.status === 201) {
              item.id = response.data.data.id
              console.log(sizes);
              for (const [key, size] of sizes) {
                console.log(key);
                console.log(size);
                delete size["isEditing"]
                size.menu_item_id = item.id;
                delete size["id"]
                this.sizeStore.add(size);
              }
              this.showCopyPopup=false
              this.getItemList()
            }
          })
      },
      search() {
        this.getItemList()
      },
      newSize(itemId) {
        let newSize = {
            "id": -1,
            "name": "",
            "price": 0,
            "quantity": 0,
            "unlimited": true,
            "index": 0,
            "isEditing": true
        }
        this.items.get(itemId).sizes.set(-1, newSize)
      },
      edit(menu_id) {
        const item = this.items.get(menu_id)
        this.items.set(item.id, { ...item, isEditing: true})
      },
      editSize(itemId, sizeId) {
        const size = this.items.get(itemId).sizes.get(sizeId)
        this.items.get(itemId).sizes.set(size.id, { ...size, isEditing: true})
      },
      cancelEdit(itemId) {
        const item = this.items.get(itemId)
        this.items.set(item.id, { ...item, isEditing: false})
      },
      cancelSizeEdit(itemId, sizeId) {
        const size = this.items.get(itemId).sizes.get(sizeId)
        this.items.get(itemId).sizes.set(size.id, { ...size, isEditing: false})
      },
      updateItem(item_id) {
        const item = this.items.get(item_id)
        this.items.set(item.id, { ...item, isEditing: false})
        delete item["isEditing"]
        delete item["sizes"]
        item.menu_id = this.$route.params.menuId
        this.itemStore.update(item.id, item)
          .then(response => {
            if (response.status === 200) {
              this.getItemList()
            }
          })
      },
      updateSize(itemId, sizeId) {
        const size = this.items.get(itemId).sizes.get(sizeId)
        this.items.get(itemId).sizes.set(size.id, { ...size, isEditing: false})
        delete size["isEditing"]
        size.menu_item_id = itemId
        if (size.id === -1) {
          delete size["id"]
          this.sizeStore.add(size)
          .then(() => {
            this.getItemList()
          })
        } else {
          this.sizeStore.update(size.id, size)
          .then(() => {
            this.getItemList()
          })

        }
      },
      deleteItem(item_id) {
        const item = this.items.get(item_id)
        this.items.set(item.id, { ...item, isEditing: false})
        this.itemStore.delete(item.id)
          .then(response => {
            if (response.status === 200) {
              this.getItemList()
            }
          })
      },
      deleteSize(itemId, sizeId) {
        const size = this.items.get(itemId).sizes.get(sizeId)
        this.items.get(itemId).sizes.set(size.id, { ...size, isEditing: false})
        this.sizeStore.delete(size.id)
          .then(() => {
            this.getItemList()
          })
      },
    }
};
</script>

<style scoped>
</style>
