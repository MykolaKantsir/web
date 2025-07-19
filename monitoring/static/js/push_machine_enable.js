const localServiceWorkerPath = "/monitoring/service-worker.js";
const localPublicKeyUrl = "/monitoring/webpush/public_key/";

// Log helper
function logToPage(label, value = null) {
    if (!window.location.search.includes("debug")) return; // Only logs when ?debug is in URL
    const logDiv = document.getElementById("debug-log");
    if (!logDiv) return;

    const msg = document.createElement("div");
    msg.innerHTML = value !== null
        ? `<strong>${label}:</strong> <code>${JSON.stringify(value, null, 2)}</code>`
        : `<strong>${label}</strong>`;
    logDiv.appendChild(msg);
    logDiv.style.display = "block";
}

// Register service worker and return registration
async function registerServiceWorker() {
    try {
        const registration = await navigator.serviceWorker.register(localServiceWorkerPath);
        logToPage("✅ Service worker registered", registration.scope);
        return registration;
    } catch (err) {
        logToPage("❌ Service worker registration failed", err.message || err);
        return null;
    }
}

// Get public key from backend
async function getPublicKey() {
    try {
        const response = await fetch(localPublicKeyUrl);
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

// Convert base64 to Uint8Array
function urlBase64ToUint8Array(base64String) {
    const padding = "=".repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
    const rawData = atob(base64);
    return new Uint8Array([...rawData].map(char => char.charCodeAt(0)));
}

// Handle checkbox interaction: ensure permission + subscribe/unsubscribe
async function handleToggle(box) {
    const eventType = box.dataset.event;
    const machine = box.dataset.machine;

    if (!("serviceWorker" in navigator)) {
        logToPage("❌ Service workers not supported");
        return;
    }

    if (!("PushManager" in window)) {
        logToPage("❌ PushManager not available in this browser");
        return;
    }

    let permission = Notification.permission;
    if (permission !== "granted") {
        permission = await Notification.requestPermission();
        logToPage("🔐 Notification permission", permission);
    }

    if (permission !== "granted") {
        logToPage("⚠️ Notifications not granted — cannot subscribe");
        box.checked = false;
        return;
    }

    const registration = await registerServiceWorker();
    if (!registration) return;

    let subscription = await registration.pushManager.getSubscription();
    if (!subscription) {
        const publicKey = await getPublicKey();
        if (!publicKey) return;

        try {
            const convertedKey = urlBase64ToUint8Array(publicKey);
            subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: convertedKey
            });
            logToPage("📦 New subscription created", subscription.toJSON());
        } catch (err) {
            logToPage("❌ Failed to subscribe", err.message || err);
            return;
        }
    }

    try {
        if (box.checked) {
            await subscribeToMachineEvent(machine, eventType, subscription);
            logToPage("✅ Subscribed to event", eventType);
        } else {
            await unsubscribeFromMachineEvent(machine, eventType, subscription);
            logToPage("🚫 Unsubscribed from event", eventType);
        }
    } catch (err) {
        logToPage("❌ Subscription API failed", err.message || err);
    }
}

// Attach event listeners to checkboxes
document.addEventListener("DOMContentLoaded", () => {
    const checkboxes = document.querySelectorAll(".subscription-toggle");
    checkboxes.forEach(box => {
        box.addEventListener("change", () => handleToggle(box));
    });

    // Hide debug log by default
    const debugLog = document.getElementById("debug-log");
    if (debugLog) debugLog.style.display = "none";
});
