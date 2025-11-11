import json

from django.conf import settings

from pywebpush import WebPushException, webpush

from .models import PushSubscription


def send_push_to_all(payload: dict) -> None:
    for subscription in PushSubscription.objects.all():
        try:
            webpush(
                subscription_info={
                    "endpoint": subscription.endpoint,
                    "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth},
                },
                data=json.dumps(payload),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims=settings.VAPID_CLAIMS,
            )
        except WebPushException:
            subscription.delete()
