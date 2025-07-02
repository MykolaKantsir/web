// service-worker.js

self.addEventListener("install", (event) => {
    self.skipWaiting(); // Activate worker immediately
});

self.addEventListener("activate", (event) => {
    // No specific activation logic for now
});

// Main push listener
self.addEventListener("push", (event) => {
    let data = {};
    
    if (event.data) {
        try {
            data = event.data.json();
        } catch (err) {
            data = { title: "Gaston Notification", body: event.data.text() || "New message received." };
        }
    }

    const title = data.title || "Gaston Notification";
    const options = {
        body: data.body || "You have a new notification.",
        icon: "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f514.png",
        badge: "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f6a8.png",
        };

    event.waitUntil(self.registration.showNotification(title, options));
});

// Optional: Notification click handling
self.addEventListener("notificationclick", (event) => {
    event.notification.close();
    event.waitUntil(clients.openWindow("/monitoring/dashboard/"));
});