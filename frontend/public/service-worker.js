// service-worker.js
console.log('Service worker script loaded');

self.addEventListener('install', () => {
  console.log('Service worker installing...');
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('Service worker activating...');
  event.waitUntil(self.clients.claim());
});

self.addEventListener('push', (event) => {
  console.log('Push event received:', event);

  if (!event.data) {
    console.log('No data in push event');
    return;
  }

  try {
    const data = event.data.json();

    event.waitUntil(
      self.registration.showNotification(data.title || 'Notification', {
        body: data.body || 'No message',
        icon: data.icon,
        image: data.image,
        tag: data.tag || 'push-notification',
        data: { url: data.url || '/' },
      })
    );
  } catch (error) {
    console.error('Error processing push event:', error);
  }
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const url = event.notification.data?.url || '/';

  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if ('navigate' in client && 'focus' in client) {
          client.navigate(url);
          return client.focus();
        }
      }
      return self.clients.openWindow(url);
    })
  );
});
