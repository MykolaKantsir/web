const serviceWorkerPath = "/monitoring/service-worker.js";  // adjust only if needed
const publicKeyUrl = "/monitoring/webpush/public_key/";

// Log helper
function logToPage(label, value = null) {
    const logDiv = document.getElementById("debug-log");
    if (!logDiv) return;

    const msg = document.createElement("div");
    msg.innerHTML = value !== null
        ? `<strong>${label}:</strong> <code>${JSON.stringify(value, null, 2)}</code>`
        : `<strong>${label}</strong>`;
    logDiv.appendChild(msg);
}

// Base64 to Uint8Array
function urlBase64ToUint8Array(base64String) {
    const padding = "=".repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
    const rawData = atob(base64);
    return new Uint8Array([...rawData].map(char => char.charCodeAt(0)));
}

// Get public key from backend
async function getPublicKey() {
    try {
        const response = await fetch(publicKeyUrl);
        const data = await response.json();
        if (data.publicKey) {
            logToPage("🔑 Public VAPID Key", data.publicKey);
            return data.publicKey;
        } else {
            throw new Error("No publicKey in response");
        }
    } catch (err) {
        logToPage("❌ Failed to fetch public key", err.message || err);
        return null;
    }
}

// Main permission handler
async function requestPushPermission() {
    if (!("serviceWorker" in navigator)) {
        logToPage("❌ Service workers not supported");
        return;
    }

    let registration;
    try {
        registration = await navigator.serviceWorker.register(serviceWorkerPath);
        logToPage("✅ Service worker registered", registration.scope);
    } catch (err) {
        logToPage("❌ Service worker registration failed", err.message || err);
        return;
    }

    if (!("PushManager" in window)) {
        logToPage("❌ PushManager not available in this browser");
        return;
    }

    const permission = await Notification.requestPermission();
    logToPage("🔐 Notification permission", permission);

    if (permission !== "granted") {
        logToPage("⚠️ Notifications not granted — cannot proceed");
        return;
    }

    let subscription = await registration.pushManager.getSubscription();

    if (!subscription) {
        const publicKey = await getPublicKey();
        if (!publicKey) return;

        const convertedKey = urlBase64ToUint8Array(publicKey);

        try {
            subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: convertedKey
            });
            logToPage("📦 New push subscription created", subscription.toJSON());
        } catch (err) {
            logToPage("❌ Failed to subscribe", err.message || err);
            return;
        }
    } else {
        logToPage("📦 Existing push subscription", subscription.toJSON());
    }

    logToPage("✅ Done. You can now receive notifications if the backend sends them.");
}

// Hook up the button
document.addEventListener("DOMContentLoaded", () => {
    const enableBtn = document.getElementById("enable-notifications");
    if (enableBtn) {
        enableBtn.addEventListener("click", requestPushPermission);
    }
});
