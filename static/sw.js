/**
 * sw.js - Service Worker for PlanSpark PWA (Version 2)
 */

// =====================================================================
// FILE: static/sw.js
// PURPOSE: Service Worker for the TaskMen PWA. Implements cache-first for static assets and network-first for dynamic requests with offline fallback.
// =====================================================================


// ---------------------------------------------------------------------
// ⬛ CACHE CONFIGURATION: Versioned cache name and static asset list
// ---------------------------------------------------------------------
// نام کش را به v2 تغییر دادیم تا مرورگر آپدیت جدید را متوجه شود
const CACHE_NAME = 'planspark-cache-v3'; 
const ASSETS_TO_CACHE = [
  // مسیر '/' را حذف کردیم تا صفحات داینامیک کش نشوند
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/icons/192.png',
  '/static/icons/512.png',
  '/static/icons/moon.svg',
  '/static/icons/sun.svg',
  '/static/offline.html'
];

// ---------------------------------------------------------------------
// ⬛ INSTALL EVENT: Pre-cache critical static assets
// ---------------------------------------------------------------------
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
  self.skipWaiting();
});

// ---------------------------------------------------------------------
// ⬛ ACTIVATE EVENT: Clean up stale cache versions
// ---------------------------------------------------------------------
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            return caches.delete(cache);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// ---------------------------------------------------------------------
// ⬛ FETCH EVENT: Routing strategy with offline fallback
// ---------------------------------------------------------------------
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        // اختیاری: فایل‌های استاتیک جدیدی که کاربر می‌بیند را به کش اضافه کن
        if (networkResponse && networkResponse.status === 200 && !event.request.url.includes('/api/')) {
          const responseClone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            // فقط فایل‌های استاتیک کش شوند، نه صفحات HTML
            if (event.request.mode !== 'navigate') {
               cache.put(event.request, responseClone);
            }
          });
        }
        return networkResponse;
      })
      .catch(() => {
        // --- اگر اینترنت قطع بود ---
        // ۱. اگر کاربر سعی کرد یک صفحه سایت (HTML) را باز کند، مستقیماً صفحه آفلاین را نشان بده
        if (event.request.mode === 'navigate') {
          return caches.match('/static/offline.html');
        }
        // ۲. برای بقیه فایل‌ها (مثل CSS و عکس‌ها)، آن‌ها را از کش بخوان
        return caches.match(event.request);
      })
  );
});