document.addEventListener("DOMContentLoaded", async () => {
    try {
        const subscription = await getCurrentSubscription();  // from push_subscription_manager.js

        if (!subscription) {
            console.warn("🔕 No active subscription found for this browser.");
            return;
        }

        const currentEndpoint = subscription.endpoint;

        // Fetch user's machine/event subscriptions
        const res = await fetch("/monitoring/my_subscriptions/", { credentials: "include" });
        const data = await res.json();

        // Pre-check checkboxes that match current browser's subscription
        data.forEach(sub => {
            if (sub.endpoint === currentEndpoint) {
                const checkbox = document.querySelector(
                    `input.subscription-toggle[data-machine="${sub.machine}"][data-event="${sub.event}"]`
                );
                if (checkbox) {
                    checkbox.checked = true;
                }
            }
        });

        // Bind click listeners to all subscription checkboxes
        document.querySelectorAll(".subscription-toggle").forEach(checkbox => {
            checkbox.addEventListener("change", async (event) => {
                const machine = checkbox.dataset.machine;
                const eventType = checkbox.dataset.event;

                if (checkbox.checked) {
                    console.log(`📬 Subscribing to ${machine} / ${eventType}`);
                    await subscribeToMachineEvent(machine, eventType, subscription);
                } else {
                    console.log(`📭 Unsubscribing from ${machine} / ${eventType}`);
                    await unsubscribeFromMachineEvent(machine, eventType, subscription);
                }
            });
        });

    } catch (err) {
        console.error("❌ Error loading subscription controls:", err);
    }
});
