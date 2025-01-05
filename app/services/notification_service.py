from pywebpush import webpush, WebPushException
from app.entities.notification import Notification
import json

from dotenv import load_dotenv
from pathlib import Path
from os import getenv
dotenv_path = Path(".env")
load_dotenv(dotenv_path=dotenv_path)

VAPID_SUBJECT = getenv("VAPID_SUBJECT_EMAIL")
VAPID_PRIVATE = getenv("VAPID_PRIVATE_KEY")

class NotificationService:

    @staticmethod
    def send_vendor_notification(vendor, order, notification_type):
        notik = Notification.find_by_vendor_id(vendor.id, notification_type)
        exclude_users = [basket.user_id for basket in order.items]
        for noti in notik:
            if noti.user_id in exclude_users:
                continue
            try:
                webpush(
                    subscription_info = {
                        "endpoint": noti.endpoint,
                        "keys": {
                            "auth": noti.auth,
                            "p256dh": noti.p256dh
                        }
                    },
                    data = json.dumps({"title": f"GroupBite - {vendor.name} rendelés hamarosan zárul", "body": f"Még nem adtál le rendelést ide: {vendor.name}"}),
                    vapid_private_key = VAPID_PRIVATE,
                    vapid_claims = { "sub": VAPID_SUBJECT }
                )
            except WebPushException as ex:
                print(f"Failed to send notification to {noti.endpoint}: {repr(ex)}")
