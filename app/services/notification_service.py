import json
import logging
from collections import defaultdict
from datetime import date
from os import getenv
from pathlib import Path

from dotenv import load_dotenv
from pywebpush import WebPushException, webpush

from app.entities.notification import Notification, NotificationType

load_dotenv(dotenv_path=Path(".env"))
VAPID_SUBJECT = getenv("VAPID_SUBJECT_EMAIL")
VAPID_PRIVATE = getenv("VAPID_PRIVATE_KEY")

log = logging.getLogger(__name__)


def _send_push(sub, title, body, vendor_id):
    try:
        webpush(
            subscription_info={
                "endpoint": sub.endpoint,
                "keys": {"auth": sub.auth, "p256dh": sub.p256dh},
            },
            data=json.dumps({
                "title": title,
                "body": body,
                "tag": str(vendor_id),
                "url": f"/menu/{urllib.parse.quote(str(sub.vendor_id))}",
            }),
            vapid_private_key=VAPID_PRIVATE,
            vapid_claims={"sub": VAPID_SUBJECT},
        )
    except WebPushException as ex:
        log.warning("Failed to send notification to %s: %s", sub.endpoint, repr(ex))


class NotificationService:

    @staticmethod
    def send_order_notifications(db, vendor, order, include_favourite=False):
        """Send all order-time notifications (REMINDER + optionally FAVOURITE) combined
        into one push per device so the user is not spammed."""
        from app.repositories.favourite_repository import FavouriteRepository
        from app.repositories.menu_item_repository import MenuItemRepository
        from app.repositories.menu_repository import MenuRepository
        from app.services.favourite_service import MATCH_THRESHOLD, _match_score

        vendor_url = f"/menu/{vendor.name}"

        # Users who already have basket items — skip all notifications for them
        users_with_items = {basket.user_id for basket in order.items}

        # Pre-compute favourite match text per user
        user_favourite_text = {}
        if include_favourite:
            today = str(date.today())
            menus = MenuRepository(db).find_active_by_vendor_id(vendor.id, today)
            all_items = []
            for menu in menus:
                all_items.extend(MenuItemRepository(db).find_all_by_menu_list([menu.id], limit=100))

            if all_items:
                all_favs = FavouriteRepository(db).find_by_vendor(vendor.id)
                user_favs = defaultdict(list)
                for fav in all_favs:
                    user_favs[fav.user_id].append(fav)

                for user_id, favs in user_favs.items():
                    if user_id in users_with_items:
                        continue
                    matched = []
                    for item in all_items:
                        for fav in favs:
                            if _match_score(fav.item_name, item.name) >= MATCH_THRESHOLD:
                                matched.append(item.name)
                                break
                    if matched:
                        user_favourite_text[user_id] = (
                            matched[0] if len(matched) == 1
                            else f"{len(matched)} kedvenced elérhető"
                        )

        # One push per device subscription — combine all applicable message parts
        for sub in Notification.find_all_by_vendor(vendor.id):
            if sub.user_id in users_with_items:
                continue

            parts = []

            if NotificationType.REMINDER in sub.notification_types:
                parts.append(f"Még nem adtál le rendelést!")

            if include_favourite and NotificationType.FAVOURITE in sub.notification_types:
                fav_text = user_favourite_text.get(sub.user_id)
                if fav_text:
                    parts.append(f"Kedvenced elérhető: {fav_text}")

            if not parts:
                continue

            try:
                webpush(
                    subscription_info={
                        "endpoint": sub.endpoint,
                        "keys": {"auth": sub.auth, "p256dh": sub.p256dh},
                    },
                    data=json.dumps({
                        "title": f"GroupBite - {vendor.name}",
                        "body": " | ".join(parts),
                        "tag": str(vendor.id),
                        "url": vendor_url,
                    }),
                    vapid_private_key=VAPID_PRIVATE,
                    vapid_claims={"sub": VAPID_SUBJECT},
                )
            except WebPushException as ex:
                log.warning("Failed to send notification to %s: %s", sub.endpoint, repr(ex))

    @staticmethod
    def send_vendor_notification(vendor, order, notification_type):
        """Legacy single-type sender — kept for any direct calls outside order flow."""
        vendor_url = f"/menu/{vendor.name}"
        exclude_users = {basket.user_id for basket in order.items}
        for noti in Notification.find_by_vendor_id(vendor.id, notification_type):
            if noti.user_id in exclude_users:
                continue
            try:
                webpush(
                    subscription_info={
                        "endpoint": noti.endpoint,
                        "keys": {"auth": noti.auth, "p256dh": noti.p256dh},
                    },
                    data=json.dumps({
                        "title": f"GroupBite - {vendor.name} rendelés hamarosan zárul",
                        "body": f"Még nem adtál le rendelést ide: {vendor.name}",
                        "tag": str(vendor.id),
                        "url": vendor_url,
                    }),
                    vapid_private_key=VAPID_PRIVATE,
                    vapid_claims={"sub": VAPID_SUBJECT},
                )
            except WebPushException as ex:
                log.warning("Failed to send notification to %s: %s", noti.endpoint, repr(ex))
