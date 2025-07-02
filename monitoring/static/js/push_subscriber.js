const publicKeyUrl = "/monitoring/webpush/public_key/";
const subscriptionUrl = "/monitoring/save_subscription/";  // backend view coming soon

async function getPublicKey() {
    const res = await fetch(publicKeyUrl);
    const data = await res.json();
    return data.publicKey;
}

async function subscribeUserToPush() {
    if (!("serviceWorker" in navigator)) {
        alert("Service Worker not supported");
        return;
    }

    const registration = await navigator.serviceWorker.register("/monitoring/service-worker.js");
    console.log("✅ Service Worker registered");

    const publicKey = await getPublicKey();
    console.log("🔑 Public key from backend:", publicKey);
    const convertedKey = urlBase64ToUint8Array(publicKey);
    console.log("🧩 Converted VAPID key (Uint8Array):", convertedKey);

    const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: convertedKey
    });

    console.log("✅ Push subscription created:", subscription);

    // Send subscription to backend
    await fetch(subscriptionUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify(subscription)
    });

    console.log("✅ Subscription sent to backend");
}

function urlBase64ToUint8Array(base64String) {
    console.log("📦 Converting VAPID public key");  // Debug log
    const padding = "=".repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/\-/g, "+").replace(/_/g, "/");
    const rawData = window.atob(base64);
    return new Uint8Array([...rawData].map(char => char.charCodeAt(0)));
}

// Automatically subscribe when the page loads
document.addEventListener("DOMContentLoaded", () => {
    subscribeUserToPush().catch(err => {
        console.error("❌ Failed to subscribe to push:", err);
    });
});
