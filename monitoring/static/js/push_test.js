// push_test.js

const serviceWorkerPath = "/monitoring/service-worker.js";
const publicKeyUrl = "/monitoring/webpush/public_key/";
const notificationUrl = "/monitoring/send_to_subscription/";

function logToPage(label, value = null) {
    const logDiv = document.getElementById("debug-log");
    if (!logDiv) return;

    const msg = document.createElement("div");
    msg.innerHTML = value !== null
        ? `<strong>${label}:</strong> <code>${JSON.stringify(value, null, 2)}</code>`
        : `<strong>${label}</strong>`;
    logDiv.appendChild(msg);
}

// Convert base64 to Uint8Array for PushManager
function urlBase64ToUint8Array(base64String) {
    const padding = "=".repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
    const rawData = atob(base64);
    return new Uint8Array([...rawData].map(c => c.charCodeAt(0)));
}

// Get public VAPID key from server
async function getPublicKey() {
    try {
        const res = await fetch(publicKeyUrl);
        const data = await res.json();
        const key = data.publicKey;
        logToPage("🔑 Public VAPID Key", key);
        return key;
    } catch (err) {
        logToPage("❌ Failed to fetch public key", err.message || err);
        throw err;
    }
}

// Register service worker + get subscription
async function requestPushPermission() {
    try {
        const registration = await navigator.serviceWorker.register(serviceWorkerPath);
        logToPage("✅ Service worker registered", registration.scope);

        const permission = await Notification.requestPermission();
        logToPage("🔐 Notification permission", permission);

        if (permission === "denied") {
            logToPage("⚠️ Notifications were explicitly denied. Please check your browser settings.");
            return;
        }

        if (permission === "default") {
            logToPage("ℹ️ Notification prompt was dismissed. User did not grant or deny.");
            return;
        }

        let subscription = await registration.pushManager.getSubscription();

        if (!subscription) {
            const publicKey = await getPublicKey();
            const convertedKey = urlBase64ToUint8Array(publicKey);

            subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: convertedKey
            });

            logToPage("📦 New subscription created", subscription.toJSON());
        } else {
            logToPage("📦 Existing subscription", subscription.toJSON());
        }

        return subscription;

    } catch (err) {
        logToPage("❌ Error during subscription", err.message || err);
    }
}

// Trigger a push using the subscription
async function sendTestNotification() {
    try {
        const registration = await navigator.serviceWorker.getRegistration(serviceWorkerPath);
        if (!registration) {
            logToPage("❌ No active service worker");
            return;
        }

        const subscription = await registration.pushManager.getSubscription();
        if (!subscription) {
            logToPage("❌ No subscription available");
            return;
        }

        const payload = {
            title: "🚨 Test Alert",
            body: "This is a test push notification from push_test.js"
        };

        const res = await fetch(notificationUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                subscription: subscription.toJSON(),
                payload: payload
            })
        });

        const result = await res.json();
        logToPage("📨 Notification send result", result);

    } catch (err) {
        logToPage("❌ Failed to send notification", err.message || err);
    }
}

// Hook up buttons
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("enable-notifications").addEventListener("click", requestPushPermission);
    document.getElementById("send-test").addEventListener("click", sendTestNotification);
});
