// KIU Admission Portal Service Worker
// Provides offline capability and caching for PWA functionality

const CACHE_NAME = 'kiu-portal-v1';
const STATIC_CACHE = 'kiu-static-v1';
const DYNAMIC_CACHE = 'kiu-dynamic-v1';

// Assets to cache immediately on install
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/images/logo.png',
  '/images/hero-bg.png',
];

// API endpoints to cache dynamically
const API_CACHE_PATTERNS = [
  /\/api\/admission\/programs/,
  /\/api\/career\/paths/,
  /\/api\/career\/my-profile/,
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker...');
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('[SW] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        console.log('[SW] Static assets cached');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('[SW] Failed to cache static assets:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker...');
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((name) => {
              return name !== STATIC_CACHE && 
                     name !== DYNAMIC_CACHE && 
                     name !== CACHE_NAME;
            })
            .map((name) => {
              console.log('[SW] Deleting old cache:', name);
              return caches.delete(name);
            })
        );
      })
      .then(() => {
        console.log('[SW] Service worker activated');
        return self.clients.claim();
      })
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Skip chrome-extension and other non-http(s) requests
  if (!url.protocol.startsWith('http')) {
    return;
  }

  // Handle API requests with network-first strategy
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirstStrategy(request));
    return;
  }

  // Handle static assets with cache-first strategy
  event.respondWith(cacheFirstStrategy(request));
});

// Cache-first strategy: serve from cache, fallback to network
async function cacheFirstStrategy(request) {
  try {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    const networkResponse = await fetch(request);
    
    // Cache successful responses
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.error('[SW] Cache-first strategy failed:', error);
    
    // Return offline fallback for navigation requests
    if (request.mode === 'navigate') {
      const offlineResponse = await caches.match('/');
      if (offlineResponse) {
        return offlineResponse;
      }
    }
    
    return new Response('Offline', { status: 503 });
  }
}

// Network-first strategy: try network, fallback to cache
async function networkFirstStrategy(request) {
  try {
    const networkResponse = await fetch(request);
    
    // Cache successful API responses
    if (networkResponse.ok) {
      const shouldCache = API_CACHE_PATTERNS.some(pattern => 
        pattern.test(request.url)
      );
      
      if (shouldCache) {
        const cache = await caches.open(DYNAMIC_CACHE);
        cache.put(request, networkResponse.clone());
      }
    }
    
    return networkResponse;
  } catch (error) {
    console.log('[SW] Network failed, trying cache:', request.url);
    
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return error response for API requests
    return new Response(
      JSON.stringify({ 
        error: 'Offline', 
        message: 'You are currently offline. Please check your internet connection.' 
      }),
      {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Background sync for form submissions
self.addEventListener('sync', (event) => {
  console.log('[SW] Background sync triggered:', event.tag);
  
  if (event.tag === 'sync-applications') {
    event.waitUntil(syncApplications());
  } else if (event.tag === 'sync-opportunity-applications') {
    event.waitUntil(syncOpportunityApplications());
  }
});

// Sync pending applications
async function syncApplications() {
  try {
    // This would sync any pending applications stored in IndexedDB
    console.log('[SW] Syncing applications...');
    // Implementation would depend on IndexedDB setup
  } catch (error) {
    console.error('[SW] Failed to sync applications:', error);
  }
}

// Sync pending opportunity applications
async function syncOpportunityApplications() {
  try {
    console.log('[SW] Syncing opportunity applications...');
    // Implementation would depend on IndexedDB setup
  } catch (error) {
    console.error('[SW] Failed to sync opportunity applications:', error);
  }
}

// Push notification handling
self.addEventListener('push', (event) => {
  console.log('[SW] Push notification received');
  
  let data = { title: 'KIU Portal', body: 'You have a new notification' };
  
  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      data.body = event.data.text();
    }
  }
  
  const options = {
    body: data.body,
    icon: '/images/logo.png',
    badge: '/images/logo.png',
    vibrate: [100, 50, 100],
    data: {
      url: data.url || '/',
    },
    actions: [
      { action: 'view', title: 'View' },
      { action: 'dismiss', title: 'Dismiss' },
    ],
  };
  
  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Notification clicked');
  
  event.notification.close();
  
  if (event.action === 'dismiss') {
    return;
  }
  
  const url = event.notification.data?.url || '/';
  
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((clientList) => {
        // Check if there's already a window open
        for (const client of clientList) {
          if (client.url.includes(self.location.origin) && 'focus' in client) {
            client.focus();
            client.navigate(url);
            return;
          }
        }
        // Open new window if none exists
        if (clients.openWindow) {
          return clients.openWindow(url);
        }
      })
  );
});

console.log('[SW] Service worker loaded');