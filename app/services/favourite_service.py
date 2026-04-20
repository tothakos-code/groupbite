import json
import logging
from collections import defaultdict
from datetime import date
from os import getenv
from pathlib import Path
from uuid import UUID, uuid4

from dotenv import load_dotenv
from pywebpush import WebPushException, webpush
from rapidfuzz import fuzz

from app.entities.notification import Notification, NotificationType
from app.entities.user_favourite import UserFavourite
from app.repositories.favourite_repository import FavouriteRepository
from app.repositories.menu_item_repository import MenuItemRepository
from app.repositories.menu_repository import MenuRepository
from app.repositories.vendor_repository import VendorRepository

load_dotenv(dotenv_path=Path(".env"))
VAPID_SUBJECT = getenv("VAPID_SUBJECT_EMAIL")
VAPID_PRIVATE = getenv("VAPID_PRIVATE_KEY")

MATCH_THRESHOLD = 84

log = logging.getLogger(__name__)


def _strip_side_dish(name: str) -> str:
    parts = name.rsplit(",", 1)
    return parts[0].strip() if len(parts) > 1 else name.strip()


def _match_score(fav_name: str, item_name: str) -> float:
    fav_full = fav_name.lower().strip()
    item_full = item_name.lower().strip()
    fav_stripped = _strip_side_dish(fav_full)
    item_stripped = _strip_side_dish(item_full)
    return max(
        fuzz.token_set_ratio(fav_full, item_full),
        fuzz.token_set_ratio(fav_stripped, item_stripped),
        fuzz.token_set_ratio(fav_full, item_stripped),
        fuzz.token_set_ratio(fav_stripped, item_full),
    )


def _load_menu_items(db, vendor_id: UUID, menu_date: str):
    menus = MenuRepository(db).find_active_by_vendor_id(vendor_id, menu_date)
    items = []
    for menu in menus:
        items.extend(MenuItemRepository(db).find_all_by_menu_list([menu.id], limit=100))
    return items


def _load_upcoming_menu_items(db, vendor_id: UUID):
    today = str(date.today())
    menus = MenuRepository(db).find_upcoming_by_vendor_id(vendor_id, today)
    items = []
    for menu in menus:
        items.extend(MenuItemRepository(db).find_all_by_menu_list([menu.id], limit=100))
    return items


def _to_uuid(val) -> UUID:
    return val if isinstance(val, UUID) else UUID(str(val))


class FavouriteService:
    @staticmethod
    def get_favourites(db, user_id, vendor_id):
        return FavouriteRepository(db).find_by_user_and_vendor(_to_uuid(user_id), _to_uuid(vendor_id))

    @staticmethod
    def get_all_favourites(db, user_id):
        return FavouriteRepository(db).find_by_user(_to_uuid(user_id))

    @staticmethod
    def add_favourite(db, user_id, vendor_id, item_name: str, threshold=MATCH_THRESHOLD):
        uid = _to_uuid(user_id)
        vid = _to_uuid(vendor_id)
        repo = FavouriteRepository(db)
        existing = repo.find_by_user_and_vendor(uid, vid)
        for fav in existing:
            if _match_score(fav.item_name, item_name) >= threshold:
                return fav
        favourite = UserFavourite(id=uuid4(), user_id=uid, vendor_id=vid, item_name=item_name)
        return repo.save(favourite)

    @staticmethod
    def remove_favourite(db, user_id, favourite_id):
        repo = FavouriteRepository(db)
        fav = repo.find_by_id(_to_uuid(favourite_id))
        if not fav:
            raise ValueError("Favourite not found")
        if fav.user_id != _to_uuid(user_id):
            raise PermissionError("Not your favourite")
        repo.delete(fav)

    @staticmethod
    def match_menu_items(db, user_id, vendor_id, menu_items, threshold=MATCH_THRESHOLD):
        """Returns {menu_item_id: favourite_id_str} for items matching a favourite."""
        favourites = FavouriteRepository(db).find_by_user_and_vendor(_to_uuid(user_id), _to_uuid(vendor_id))
        if not favourites:
            return {}
        result = {}
        for item in menu_items:
            item_name = item.name if hasattr(item, "name") else item["name"]
            item_id = item.id if hasattr(item, "id") else item["id"]
            best_score = 0
            best_fav = None
            for fav in favourites:
                score = _match_score(fav.item_name, item_name)
                if score > best_score:
                    best_score = score
                    best_fav = fav
            if best_score >= threshold:
                result[item_id] = str(best_fav.id)
        return result

    @staticmethod
    def get_matches_for_date(db, user_id, vendor_id, menu_date: str, threshold=MATCH_THRESHOLD):
        items = _load_menu_items(db, _to_uuid(vendor_id), menu_date)
        return FavouriteService.match_menu_items(db, user_id, vendor_id, items, threshold)

    @staticmethod
    def notify_on_new_favourite(db, user_id, vendor_id, item_name, threshold=MATCH_THRESHOLD):
        """Send push notifications to the user if the newly added favourite matches any upcoming menu items."""
        uid = _to_uuid(user_id)
        vid = _to_uuid(vendor_id)

        all_items = _load_upcoming_menu_items(db, vid)
        if not all_items:
            return

        matched_names = [item.name for item in all_items if _match_score(item_name, item.name) >= threshold]
        if not matched_names:
            return

        vendor = VendorRepository(db).get_by_id(vid)
        if not vendor:
            return

        subscriptions = Notification.find_by_vendor_id_user_id(vid, uid, NotificationType.FAVOURITE)
        if not subscriptions:
            return

        vendor_url = f"/menu/{vendor.name}"
        body = matched_names[0] if len(matched_names) == 1 else f"{len(matched_names)} kedvenced elérhető"
        for noti in subscriptions:
            try:
                webpush(
                    subscription_info={
                        "endpoint": noti.endpoint,
                        "keys": {"auth": noti.auth, "p256dh": noti.p256dh},
                    },
                    data=json.dumps({
                        "title": f"GroupBite - {vendor.name}",
                        "body": f"Kedvenced elérhető: {body}",
                        "tag": str(vid),
                        "url": vendor_url,
                    }),
                    vapid_private_key=VAPID_PRIVATE,
                    vapid_claims={"sub": VAPID_SUBJECT},
                )
            except WebPushException as ex:
                log.warning("Failed to send favourite notification to %s: %s", noti.endpoint, repr(ex))

    @staticmethod
    def send_favourite_notifications(db, vendor, order=None, threshold=MATCH_THRESHOLD):
        from app.repositories.user_basket_repository import UserBasketRepository

        today = str(date.today())
        all_items = _load_menu_items(db, vendor.id, today)
        if not all_items:
            return

        all_favs = FavouriteRepository(db).find_by_vendor(vendor.id)
        user_favs = defaultdict(list)
        for fav in all_favs:
            user_favs[fav.user_id].append(fav)

        basket_repo = UserBasketRepository(db) if order is not None else None

        for user_id, favs in user_favs.items():
            matched_names = []
            for item in all_items:
                for fav in favs:
                    if _match_score(fav.item_name, item.name) >= threshold:
                        matched_names.append(item.name)
                        break
            if not matched_names:
                continue

            if basket_repo is not None:
                basket = basket_repo.find_user_basket(order.id, user_id)
                if basket:
                    log.info("Skipping favourite notification for user %s: basket is not empty", user_id)
                    continue

            subscriptions = Notification.find_by_vendor_id_user_id(
                vendor.id, user_id, NotificationType.FAVOURITE
            )
            vendor_url = f"/menu/{vendor.name}"
            body = (
                matched_names[0]
                if len(matched_names) == 1
                else f"{len(matched_names)} kedvenced elérhető"
            )
            for noti in subscriptions:
                try:
                    webpush(
                        subscription_info={
                            "endpoint": noti.endpoint,
                            "keys": {"auth": noti.auth, "p256dh": noti.p256dh},
                        },
                        data=json.dumps(
                            {
                                "title": f"GroupBite - {vendor.name}",
                                "body": f"Kedvenced elérhető: {body}",
                                "tag": str(vendor.id),
                                "url": vendor_url,
                            }
                        ),
                        vapid_private_key=VAPID_PRIVATE,
                        vapid_claims={"sub": VAPID_SUBJECT},
                    )
                except WebPushException as ex:
                    log.warning(
                        "Failed to send favourite notification to %s: %s",
                        noti.endpoint,
                        repr(ex),
                    )
