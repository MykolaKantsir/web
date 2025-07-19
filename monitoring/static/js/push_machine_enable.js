const localServiceWorkerPath = "/monitoring/service-worker.js"; 
const localPublicKeyUrl = "/monitoring/webpush/public_key/";

// Log helper (only logs when ?debug is present in URL)
function logToPage(label, value = null) {
    if (!window.location.search.includes("debug")) return;

    const logDiv = document.getElementById("debug-log");
    if (!logDiv) return;

    const msg = document.createElement("div");
    msg.innerHTML = value !== null
        ? `<strong>${label}:</strong> <code>${JSON.stringify(value, null, 2)}</code>`
        : `<strong>${label}</strong>`;
    logDiv.appendChild(msg);
    logDiv.style.display = "block"; // Show the log if it was hidden
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

// Request permission and handle registration/subscription if needed
async function requestPushPermissionIfNeeded() {
    if (!("serviceWorker" in navigator)) {
        logToPage("❌ Service workers not supported");
        return null;
    }

    try {
        const registration = await navigator.serviceWorker.register(localServiceWorkerPath);
        logToPage("✅ Service worker registered", registration.scope);

        if (!("PushManager" in window)) {
            logToPage("❌ PushManager not available in this browser");
            return null;
        }

        let subscription = await registration.pushManager.getSubscription();

        if (!subscription) {
            const permission = await Notification.requestPermission();
            logToPage("🔐 Notification permission", permission);

            if (permission !== "granted") {
                logToPage("⚠️ Notifications not granted — cannot proceed");
                return null;
            }

            const publicKey = await getPublicKey();
            if (!publicKey) return null;

            const convertedKey = urlBase64ToUint8Array(publicKey);

            try {
                subscription = await registration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: convertedKey
                });
                logToPage("📦 New push subscription created", subscription.toJSON());
            } catch (err) {
                logToPage("❌ Failed to subscribe", err.message || err);
                return null;
            }
        } else {
            logToPage("📦 Existing push subscription", subscription.toJSON());
        }

        return subscription;
    } catch (err) {
        logToPage("❌ Error during service worker registration", err.message || err);
        return null;
    }
}

// Listen to checkbox toggles and request permission if needed
document.addEventListener("DOMContentLoaded", () => {
    const checkboxes = document.querySelectorAll(".subscription-toggle");
    checkboxes.forEach(box => {
        box.addEventListener("click", async () => {
            if (Notification.permission !== "granted") {
                await requestPushPermissionIfNeeded();
            }
        });
    });

    // Hide log by default unless ?debug is in URL
    const debugLog = document.getElementById("debug-log");
    if (debugLog && !window.location.search.includes("debug")) {
        debugLog.style.display = "none";
    }
});
