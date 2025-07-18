from monitoring.models import MachineSubscription
from pywebpush import webpush, WebPushException
import json
from django.conf import settings


# Monitoring and push notification functions
def send_push_to_subscribers(machine, event_type, payload: dict):
    subscriptions = MachineSubscription.objects.filter(
        machine=machine,
        event_type=event_type,
        subscription__is_active=True
    ).select_related("subscription")

    for sub in subscriptions:
        subscription = sub.subscription
        try:
            webpush(
                subscription_info={
                    "endpoint": subscription.endpoint,
                    "keys": {
                        "p256dh": subscription.public_key,
                        "auth": subscription.auth_key,
                    },
                },
                data=json.dumps(payload),
                vapid_private_key=settings.WEBPUSH_PRIVATE_KEY,
                vapid_claims={"sub": "mailto:admin@example.com"},
            )
            print(f"📨 Notification sent to {subscription}")
        except WebPushException as e:
            print(f"❌ Failed push, marking inactive: {e}")
            subscription.is_active = False
            subscription.save()

# Test fuction to send push notifications to a raw subscription object
# this was used to test on apple devices
def send_push_to_raw_subscription(subscription_info: dict, payload: dict):
    """
    Sends a push notification to a raw subscription object (no DB lookup).

    Args:
        subscription_info (dict): A dict with 'endpoint' and 'keys' for 'p256dh' and 'auth'.
        payload (dict): The notification payload to send.
    
    Returns:
        dict: Status information.
    """
    try:
        response = webpush(
            subscription_info=subscription_info,
            data=json.dumps(payload),
            vapid_private_key=settings.WEBPUSH_PRIVATE_KEY,
            vapid_claims={"sub": "mailto:admin@example.com"},
        )
        return {"status": "success", "details": str(response)}
    except WebPushException as e:
        return {
            "status": "error",
            "message": str(e),
            "response": getattr(e, 'response', None),
        }