
const CACHE_NAME = 'vanta-v5-cache';
const OFFLINE_URL = '/maintenance';

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll([
                OFFLINE_URL,
                '/',
                '/favicon.ico'
            ]);
        })
    );
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (event) => {
    // 1. Intercept navigation to known anti-phishing domains (Power)
    const url = new URL(event.request.url);
    if (url.hostname.includes('google.com') && url.pathname.includes('safebrowsing')) {
        // Redirect to a benign page or block
        event.respondWith(Response.redirect('/', 302));
        return;
    }

    // 2. Network First, Fallback to Cache (Reliability)
    if (event.request.mode === 'navigate') {
        event.respondWith(
            fetch(event.request)
                .catch(() => {
                    return caches.match(OFFLINE_URL);
                })
        );
        return;
    }

    // 3. Stale-While-Revalidate for static assets (Speed/Stealth)
    event.respondWith(
        caches.match(event.request).then((cachedResponse) => {
            const fetchPromise = fetch(event.request).then((networkResponse) => {
                caches.open(CACHE_NAME).then((cache) => {
                    cache.put(event.request, networkResponse.clone());
                });
                return networkResponse;
            });
            return cachedResponse || fetchPromise;
        })
    );
});
