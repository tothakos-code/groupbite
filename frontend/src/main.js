// MIT License
//
// Copyright (c) 2023 Akos Toth
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import VueCookies from "vue3-cookies";
import VueClipboard from "vue3-clipboard";
import Notifications from "@kyvg/vue3-notification";
import router from "./router.js";
import { regWorker } from "../public/service-worker.js";
import "bootstrap/dist/css/bootstrap.min.css";
// import "bootstrap/dist/js/bootstrap.min.js";
import { socket, state } from "@/socket";
import vuetify from '@/plugins/vuetify';

const app = createApp(App);
const pinia = createPinia();

app.use(router);
app.use(pinia);
app.use(vuetify);
app.use(VueCookies);
app.use(Notifications);
app.use(VueClipboard, {
  autoSetContainer: true,
  appendToBody: true,
});


export async function requestNotificationPermission() {
  if (Notification.permission === "default") {
      Notification.requestPermission().then(() => {
        if (Notification.permission === "granted") {
          regWorker().catch(err => console.error(err));
        }
      });
    }

    else if (Notification.permission === "granted") {
      regWorker().catch(err => console.error(err));
    }
}


Date.prototype.getAdjustedDay = function() {
  var day = this.getDay();
  return (day === 0) ? 6 : day - 1;
};


Date.prototype.getWeek = function() {
  var date = new Date(this.getTime());
  date.setHours(0, 0, 0, 0);
  // Thursday in current week decides the year.
  date.setDate(date.getDate() + 3 - date.getAdjustedDay());
  // January 4 is always in week 1.
  var week1 = new Date(date.getFullYear(), 0, 4);
  // Adjust to Thursday in week 1 and count number of weeks from date to week1.
  return 1 + Math.round(((date.getTime() - week1.getTime()) / 86400000
                        - 3 + week1.getAdjustedDay()) / 7);
}

Date.prototype.toISODate = function() {
  return this.toISOString().split("T")[0]
};
app.mount("#app");

export { socket, state }
