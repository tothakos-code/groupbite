export async function regWorker () {

  navigator.serviceWorker.register("/service-worker.js", { scope: "/" });

self.addEventListener("install", () => self.skipWaiting());

self.addEventListener("activate", () => self.clients.claim());

self.addEventListener("push", event => {
  const data = event.data.json();
  self.registration.showNotification(data.title, {
    body: data.body,
    icon: data.icon,
    image: data.image
  });
});
}
