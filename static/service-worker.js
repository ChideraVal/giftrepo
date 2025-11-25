// 🧱 Change this version whenever you update your game files
const CACHE_NAME = 'bixy-cache-v2';

const STATIC_ASSETS = [
  '/offline/',
  '/loading/',
  // '/signin/',
  // '/signup/',
  // '/static/css/signin.css',
  // '/static/css/signup.css',
  '/static/css/all_gifts.css',
  '/static/css/main.css',
  '/static/css/ads.css',
  '/static/css/reveal.css',
  // '/static/css/verify.css',
  // '/static/scripts/buygift.js',
  // '/static/scripts/payearlyreveal.js',
  // '/static/scripts/sparkles.js',
  // '/static/scripts/timer.js',
  // '/static/images/balloons.gif',
  // '/static/images/balloons.png',
  // '/static/images/bear.png',
  // '/static/images/bird.png',
  // '/static/images/cake.gif',
  // '/static/images/cake.png',
  // '/static/images/candy.gif',
  // '/static/images/candy.png',
  // '/static/images/cat.png',
  // '/static/images/check.png',
  // '/static/images/chick.png',
  // '/static/images/diamond.gif',
  // '/static/images/diamond.png',
  // '/static/images/dollar.gif',
  '/static/images/dollar.png',
  // '/static/images/dragon.gif',
  // '/static/images/dragon.png',
  // '/static/images/elephant.png',
  // '/static/images/empty-box.png',
  // '/static/images/frog.png',
  // '/static/images/gem.gif',
  // '/static/images/gem.png',
  // '/static/images/gift-box.png',
  // '/static/images/giftbox (1).png',
  // '/static/images/heart (1).png',
  // '/static/images/heart (2).png',
  // '/static/images/hibiscus-flower.gif',
  // '/static/images/hibiscus-flower.png',
  // '/static/images/key.gif',
  '/static/images/key.png',
  // '/static/images/microphone.gif',
  // '/static/images/microphone.png',
  // '/static/images/moon.gif',
  // '/static/images/pending.png',
  // '/static/images/pizza-delivery.gif',
  // '/static/images/pizza-delivery.png',
  // '/static/images/rabbit.png',
  // '/static/images/rocket.gif',
  // '/static/images/rocket.png',
  // '/static/images/sad (1).png',
  // '/static/images/search.gif',
  // '/static/images/search.png',
  // '/static/images/sloth.png',
  // '/static/images/smiling.png',
  // '/static/images/teddy-bear.png',
  // '/static/images/trophy.gif',
  // '/static/images/trophy.png',
  // '/static/images/user (3).png',
  '/static/images/user.png',
  // '/static/images/wallet.png',
  // '/static/images/x-button.png',
  // '/static/manifest.json',
  // 'https://fonts.googleapis.com/css2?family=Passion+One:wght@400;700;900&display=swap',
  // 'https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,100..1000;1,9..40,100..1000&display=swap'
];

// 🧩 Install phase — pre-cache static assets
self.addEventListener('install', event => {
  console.log('[Service Worker] Installing new version:', CACHE_NAME);
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      cache.addAll(STATIC_ASSETS).then(
        cache.keys().then(keys => {
          console.log("SW CACHED SUCCESSULLY:", keys)
        })
      )
    })
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
  // console.log("Cached static assets:")
  // event.waitUntil(
  //   caches.open(CACHE_NAME).then(cache => {
  //     cache.keys().then(keys => {
  //       console.log(keys)
  //     })
  //   })
  // )


  const url = new URL(event.request.url);


  if (url.pathname === '/loading/') {
    return;
  }

  if (event.request.method !== 'GET') {
    console.log('MAKING POST REQUEST.', event.request.url)
    event.respondWith(fetch(event.request).catch(() => {
      // return offline page for post requests
      return caches.match('/offline/')
    }));
    return
  }

  if (event.request.mode === "navigate" && !url.pathname.startsWith('/admin/') && !url.pathname.startsWith('/logout/') && !url.pathname.startsWith('/signin/') && !url.pathname.startsWith('/signup/')) {
    console.log("LOADING NAVIGATE...", url.pathname)
    event.respondWith(caches.match('/loading/'));
    return;
  }

  // 🧠 Never cache the highscore API
  // console.log("URL PATHNAME (not auth/static):", url.pathname)
  console.log('PRESENCE OF :', url.pathname, ':', STATIC_ASSETS.includes(url.pathname))
  if (!STATIC_ASSETS.includes(url.pathname)) {
  // if (!url.pathname.startsWith('/signin/') && !url.pathname.startsWith('/signup/') && !STATIC_ASSETS.includes(url.pathname)) {
    // console.log('GET FRESH DATA.', url.pathname)
    event.respondWith(fetch(event.request)
      .catch(() => {
        // return offline page for post requests
        return caches.match('/offline/')
      })
    );
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

  // console.log("Cached static assets:", caches.keys().then(cached => {
  //   console.log(cached)
  // }))




  // console.log("URL PATHNAME (auth/static):", url.pathname)
  event.respondWith(
    caches.match(url.pathname, { ignoreSearch: true }).then(cached => {
      // console.log('GETTING FROM CACHE (auth/static).', url.pathname)
      return (
        cached ||
        fetch(event.request).then(response => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          console.log('SAVED FRESH CONTENT TO CACHE (auth/static).', url.pathname)
          return response;
        })
      );
    })
  );
});
