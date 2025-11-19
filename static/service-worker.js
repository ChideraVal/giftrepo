// 🧱 Change this version whenever you update your game files
const CACHE_NAME = 'bixy-cache-v2';

const STATIC_ASSETS = [
  '/',
  '/signin/',
  '/signup/',
  '/gifts/send/',
];

// 🧩 Install phase — pre-cache static assets
self.addEventListener('install', event => {
  console.log('[Service Worker] Installing new version:', CACHE_NAME);
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting(); // Activate immediately after install
});

// 🧹 Activate phase — remove old caches
self.addEventListener('activate', event => {
  console.log('[Service Worker] Activating and cleaning old caches...');
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(key => key !== CACHE_NAME)
          .map(key => caches.delete(key))
      )
    )
  );
  self.clients.claim(); // Control all clients right away
});

// ⚙️ Fetch phase — define caching strategies
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // 🧠 Never cache the highscore API
  // console.log(url.pathname)
  if (url.pathname === '/all-gifts/' || url.pathname === '/send-gift/') {
    console.log('GET FRESH DATA.', url.pathname)
    event.respondWith(fetch(event.request));
    return;
  }

  // 🧠 Network-first for main page
  // if (url.pathname === '/game1/index.html' || url.pathname === '/game1/') {
  //   event.respondWith(
  //     fetch(event.request)
  //       .then(response => {
  //         const clone = response.clone();
  //         caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
  //         return response; // ✅ Always fresh when online
  //       })
  //       .catch(() => caches.match(event.request)) // 🔁 Use cache when offline
  //   );
  //   return;
  // }

  // 🧠 Cache-first for other static assets
  event.respondWith(
    caches.match(url.pathname, {ignoreSearch: true}).then(cached => {
      console.log('GETTING FROM CACHE.', url.pathname)
      return (
        cached ||
        fetch(event.request).then(response => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          console.log('SAVED FRESH CONTENT TO CACHE.', url.pathname)
          return response;
        })
      );
    })
  );
});
