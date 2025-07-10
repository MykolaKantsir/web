self.addEventListener("install", (event) => {
    self.skipWaiting(); // Activate worker immediately
});

self.addEventListener("activate", (event) => {
    // No specific activation logic needed for now
});

// Main push notification handler
self.addEventListener("push", (event) => {
    let data = {};

    if (event.data) {
        try {
            data = event.data.json();
        } catch (err) {
            data = {
                title: "Gaston Notification",
                body: event.data.text() || "New message received."
            };
        }
    }

    const title = data.title || "Gaston Notification";
    const options = {
        body: data.body || "You have a new notification.",
        icon: "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f514.png",
        badge: "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f6a8.png",
        data: {
            machine_id: data.machine_id
        }
    };

    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

// Handle click on notification
self.addEventListener("notificationclick", (event) => {
    event.notification.close();

    const machineId = event.notification.data?.machine_id;

    const targetUrl = machineId
        ? `/monitoring/machine-subscribe/${machineId}/`
        : `/monitoring/dashboard`;  // fallback if no ID

    event.waitUntil(
        clients.openWindow(targetUrl)
    );
});
