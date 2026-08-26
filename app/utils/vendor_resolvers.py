"""Resolver callables for `require_vendor_manager`.

Each resolver takes `(db, **kwargs)` (kwargs being the Flask view's URL params, already
validated by `validate_url_params`) and returns the `vendor_id` the request is scoped to,
or `None` if it can't be resolved. `kwargs` alone is enough for routes where `vendor_id`
(or a parent object's id) is a URL param; routes where it's in the query string or JSON
body read `flask.request` directly instead.
"""

from flask import request

from app.repositories.menu_item_repository import MenuItemRepository
from app.repositories.menu_repository import MenuRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.size_repository import SizeRepository
from app.repositories.webhook_repository import WebhookRepository


def vendor_from_kwarg(name="vendor_id"):
    def resolver(db, **kwargs):
        return kwargs.get(name)
    return resolver


def vendor_from_query(name="vendor_id"):
    def resolver(db, **kwargs):
        return request.args.get(name)
    return resolver


def vendor_from_body(name="vendor_id"):
    def resolver(db, **kwargs):
        body = request.get_json(silent=True) or {}
        data = body.get("data", body)
        return data.get(name)
    return resolver


def vendor_from_menu(param="menu_id"):
    def resolver(db, **kwargs):
        menu = MenuRepository(db).get_by_id(kwargs.get(param))
        return menu.vendor_id if menu else None
    return resolver


def vendor_from_menu_item(param="item_id"):
    def resolver(db, **kwargs):
        item = MenuItemRepository(db).get_by_id(kwargs.get(param))
        return item.menu.vendor_id if item and item.menu else None
    return resolver


def vendor_from_body_menu_item(field="menu_item_id"):
    def resolver(db, **kwargs):
        body = request.get_json(silent=True) or {}
        data = body.get("data", body)
        item = MenuItemRepository(db).get_by_id(data.get(field))
        return item.menu.vendor_id if item and item.menu else None
    return resolver


def vendor_from_size(param="size_id"):
    def resolver(db, **kwargs):
        size = SizeRepository(db).get_by_id(kwargs.get(param))
        if not size or not size.menu_item:
            return None
        return size.menu_item.menu.vendor_id if size.menu_item.menu else None
    return resolver


def vendor_from_webhook(param="webhook_id"):
    def resolver(db, **kwargs):
        webhook = WebhookRepository(db).find_by_id(kwargs.get(param))
        return webhook.vendor_id if webhook else None
    return resolver


def vendor_from_order(param="order_id"):
    def resolver(db, **kwargs):
        order = OrderRepository(db).get_by_id(kwargs.get(param))
        return order.vendor_id if order else None
    return resolver


def _single_vendor_for_items(db, item_ids):
    """Resolves the one vendor all given item_ids belong to, or None if the list is empty,
    any id doesn't exist, or the ids span more than one vendor (fail closed)."""
    vendor_id = None
    for item_id in item_ids:
        item = MenuItemRepository(db).get_by_id(item_id)
        if not item or not item.menu:
            return None
        if vendor_id is None:
            vendor_id = item.menu.vendor_id
        elif item.menu.vendor_id != vendor_id:
            return None
    return vendor_id


def _single_vendor_for_sizes(db, size_ids):
    vendor_id = None
    for size_id in size_ids:
        size = SizeRepository(db).get_by_id(size_id)
        if not size or not size.menu_item or not size.menu_item.menu:
            return None
        v = size.menu_item.menu.vendor_id
        if vendor_id is None:
            vendor_id = v
        elif v != vendor_id:
            return None
    return vendor_id


def vendor_from_body_items_or_menu(items_field="item_ids", menu_field="select_all_menu_id"):
    """For bulk item routes taking either a list of item_ids or a single select_all_menu_id."""
    def resolver(db, **kwargs):
        body = request.get_json(silent=True) or {}
        data = body.get("data", body)
        menu_id = data.get(menu_field)
        if menu_id is not None:
            menu = MenuRepository(db).get_by_id(menu_id)
            return menu.vendor_id if menu else None
        return _single_vendor_for_items(db, data.get(items_field) or [])
    return resolver


def vendor_from_body_item_list(field="items", id_key="id"):
    """For bulk routes whose body is a list of dicts each carrying a menu item id."""
    def resolver(db, **kwargs):
        body = request.get_json(silent=True) or {}
        data = body.get("data", body)
        item_ids = [row.get(id_key) for row in (data.get(field) or [])]
        return _single_vendor_for_items(db, item_ids)
    return resolver


def vendor_from_body_size_list(field="sizes", id_key="id"):
    """For bulk routes whose body is a list of dicts each carrying a size id."""
    def resolver(db, **kwargs):
        body = request.get_json(silent=True) or {}
        data = body.get("data", body)
        size_ids = [row.get(id_key) for row in (data.get(field) or [])]
        return _single_vendor_for_sizes(db, size_ids)
    return resolver
