// Minimal Service Worker for PWA installability
const CACHE_NAME = 'sous-chef-v2';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (event) => {
  // Let network handle API and fast polling requests
  if (event.request.url.includes('/api/') || event.request.url.includes('/alexa') || event.request.url.includes('/mcp')) {
    return;
  }
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});
