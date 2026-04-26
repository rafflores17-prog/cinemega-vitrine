/* ==========================================
   CÓDIGO DO MONETAG (Validação e Anúncios)
   ========================================== */
self.options = {
    "domain": "3nbf4.com",
    "zoneId": 10919957
};
self.lary = "";
importScripts('https://3nbf4.com/act/files/service-worker.min.js?r=sw');

/* ==========================================
   CÓDIGO DO SEU PWA (Cache e Offline)
   ========================================== */
const CACHE_NAME = 'cinemega-v3'; 
const ASSETS_TO_CACHE = [
  '/',
  '/manifest.json',           // ✅ Manifest na raiz
  '/static/icon-192.png',     // ✅ Ícone dentro de static
  '/static/icon-512.png'      // ✅ Ícone dentro de static
];

// Instalação do Cache
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache do Cine Mega instalado com sucesso!');
        return cache.addAll(ASSETS_TO_CACHE);
      })
  );
  self.skipWaiting();
});

// Limpeza de caches antigos
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Interceptação de requisições
self.addEventListener('fetch', event => {
  // Ignora o Monetag para não travar os anúncios
  if (event.request.url.includes('3nbf4.com')) {
    return;
  }

  event.respondWith(
    fetch(event.request).catch(() => {
      return caches.match(event.request);
    })
  );
});
