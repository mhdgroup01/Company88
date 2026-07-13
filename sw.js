/* Borisat service worker — app shell offline-first */
const VERSION = 'borisat-v4';
const FONT_CACHE = 'borisat-fonts-v1';
const SHELL = [
  './',
  './index.html',
  './manifest.json',
  './icons/emblem-police.svg',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable-512.png',
  './icons/apple-touch-icon.png',
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      // ลบเฉพาะ cache ของ borisat เอง — CacheStorage เป็น per-origin
      // ถ้า deploy ร่วม origin กับแอปอื่น (เช่น parme.me) ห้ามลบของเขา
      .then(keys => Promise.all(keys.filter(k => k.startsWith('borisat-') && k !== VERSION && k !== FONT_CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET') return;

  // ฟอนต์ Google — stale-while-revalidate ลง cache แยก
  // (รับ opaque ด้วย เผื่อ request ที่หลุดมาแบบ no-cors)
  if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    e.respondWith(
      caches.open(FONT_CACHE).then(async c => {
        const hit = await c.match(e.request);
        const net = fetch(e.request).then(res => {
          if (res.ok || res.type === 'opaque') c.put(e.request, res.clone());
          return res;
        }).catch(() => hit);
        e.waitUntil(net.catch(() => {}));
        return hit || net;
      })
    );
    return;
  }

  if (url.origin !== location.origin) return;

  // หน้าเอกสาร — network-first fallback cache
  // เก็บทับ './index.html' เฉพาะ response ของหน้าแอปจริงที่สมบูรณ์เท่านั้น
  // (กัน captive portal / 404 / redirect วางยา app shell)
  if (e.request.mode === 'navigate') {
    e.respondWith(
      fetch(e.request).then(res => {
        const scopePath = new URL(self.registration.scope).pathname;
        const okShell = res.ok && !res.redirected &&
          (url.pathname === scopePath || url.pathname === scopePath + 'index.html');
        if (okShell) {
          const copy = res.clone();
          e.waitUntil(caches.open(VERSION).then(c => c.put('./index.html', copy)));
        }
        return res;
      }).catch(() => caches.match('./index.html'))
    );
    return;
  }

  // ไฟล์อื่น (ไอคอน ฯลฯ) — cache-first + อัปเดตเบื้องหลัง
  e.respondWith(
    caches.match(e.request).then(hit => {
      const net = fetch(e.request).then(res => {
        if (res.ok && !res.redirected) {
          const copy = res.clone();
          e.waitUntil(caches.open(VERSION).then(c => c.put(e.request, copy)));
        }
        return res;
      }).catch(() => hit);
      if (hit) e.waitUntil(net.catch(() => {}));
      return hit || net;
    })
  );
});
