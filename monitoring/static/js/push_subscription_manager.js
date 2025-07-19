const publicKeyUrl = "/monitoring/webpush/public_key/";
const subscribeUrl = "/monitoring/subscribe_machine/";
const unsubscribeUrl = "/monitoring/unsubscribe_machine/";
const serviceWorkerPath = "/monitoring/service-worker.js";

// Fetch the VAPID public key from the backend
async function getPublicKey() {
    const res = await fetch(publicKeyUrl);
    const data = await res.json();
    return data.publicKey;
}

// Convert base64 string to Uint8Array for PushManager
function urlBase64ToUint8Array(base64String) {
    const padding = "=".repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
    const rawData = atob(base64);
    return new Uint8Array([...rawData].map(char => char.charCodeAt(0)));
}

// Register service worker and return the push subscription object (creates if needed)
async function getCurrentSubscription() {
    try {
        const registration = await navigator.serviceWorker.register(serviceWorkerPath);
        let subscription = await registration.pushManager.getSubscription();

        if (!subscription) {
            const permission = await Notification.requestPermission();
            if (permission === "granted") {
                const publicKey = await getPublicKey();
                const convertedKey = urlBase64ToUint8Array(publicKey);
                subscription = await registration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: convertedKey
                });
            }
        }

        return subscription;
    } catch (err) {
        console.error("Error during getCurrentSubscription:", err);
        return null;
    }
}

// Send the current subscription + event to the backend to save it
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

// Inform backend to remove a subscription for a machine + event
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

// Export utility functions for other JS files
window.getCurrentSubscription = getCurrentSubscription;
window.subscribeToMachineEvent = subscribeToMachineEvent;
window.unsubscribeFromMachineEvent = unsubscribeFromMachineEvent;
