function logToPage(label, value = null) {
    const logDiv = document.getElementById("debug-log");
    if (!logDiv) return;

    const msg = document.createElement("div");
    msg.innerHTML = value !== null
        ? `<strong>${label}:</strong> <code>${JSON.stringify(value, null, 2)}</code>`
        : `<strong>${label}</strong>`;
    logDiv.appendChild(msg);
}

const publicKeyUrl = "/monitoring/webpush/public_key/";
const subscribeUrl = "/monitoring/subscribe_machine/";
const unsubscribeUrl = "/monitoring/unsubscribe_machine/";
const serviceWorkerPath = "/monitoring/service-worker.js";

// Get the VAPID public key from the backend
async function getPublicKey() {
    const res = await fetch(publicKeyUrl);
    const data = await res.json();
    return data.publicKey;
}

// Convert base64 to Uint8Array for PushManager
function urlBase64ToUint8Array(base64String) {
    const padding = "=".repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
    const rawData = atob(base64);
    return new Uint8Array([...rawData].map(char => char.charCodeAt(0)));
}

// Register service worker + get existing or new subscription
async function getCurrentSubscription() {
    logToPage("📍 Entered getCurrentSubscription()");

    if (!("serviceWorker" in navigator)) {
        logToPage("❌ Service workers not supported in this browser.");
        return null;
    }

    logToPage("✅ navigator.serviceWorker is available", navigator.serviceWorker);

    try {
        const registration = await navigator.serviceWorker.register(serviceWorkerPath);
        logToPage("✅ Service worker registered", registration);

        logToPage("⏳ Checking registration.pushManager...");
        if (!registration.pushManager) {
            logToPage("❌ registration.pushManager is undefined");
            return null;
        } else {
            logToPage("✅ registration.pushManager is available", registration.pushManager);
        }

        let subscription = await registration.pushManager.getSubscription();
        logToPage("📦 subscription from pushManager.getSubscription()", subscription);

        if (!subscription) {
            logToPage("📭 No existing subscription, requesting permission...");
            const permission = await Notification.requestPermission();
            logToPage("🔐 Notification.requestPermission() result", permission);

            if (permission === "granted") {
                const publicKey = await getPublicKey();
                const convertedKey = urlBase64ToUint8Array(publicKey);
                subscription = await registration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: convertedKey
                });
                logToPage("✅ New subscription created", subscription);
            } else {
                logToPage("❌ Notification permission was not granted");
            }
        } else {
            logToPage("📦 Re-using existing push subscription");
        }

        return subscription;

    } catch (err) {
        logToPage("❌ Error during service worker or subscription setup", err.message || err);
        return null;
    }
}

// Send subscription + machine/event info to backend
async function subscribeToMachineEvent(machine, eventType, subscription) {
    const res = await fetch(subscribeUrl, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            machine,
            event_type: eventType,
            subscription
        })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Subscription failed");
    console.log("📬 Subscribed successfully:", data);
}

// Remove subscription from machine/event
async function unsubscribeFromMachineEvent(machine, eventType, subscription) {
    const res = await fetch(unsubscribeUrl, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            machine,
            event_type: eventType,
            subscription
        })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Unsubscribe failed");
    console.log("📭 Unsubscribed successfully:", data);
}

// Export functions globally (optional if using modules)
window.getCurrentSubscription = getCurrentSubscription;
window.subscribeToMachineEvent = subscribeToMachineEvent;
window.unsubscribeFromMachineEvent = unsubscribeFromMachineEvent;
