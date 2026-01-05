from marshmallow import Schema, ValidationError, fields, validate

from app.db.session import get_session
from app.entities.menu import Menu
from app.entities.menu_item import MenuItem
from app.entities.notification import NotificationType
from app.entities.order import Order
from app.entities.size import Size
from app.entities.user import User
from app.entities.vendor import Vendor
from app.entities.webhook import Webhook
from app.repositories.menu_item_repository import MenuItemRepository
from app.repositories.menu_repository import MenuRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.size_repository import SizeRepository
from app.repositories.user_repository import UserRepository
from app.repositories.vendor_repository import VendorRepository
from app.repositories.webhook_repository import WebhookRepository


def validate_order_id(order_id):
    with get_session() as db:
        exists = OrderRepository(db).get_by_id(order_id) is not None
    if not exists:
        raise ValidationError(f"Order with ID {order_id} does not exist.")


def validate_user_id(user_id):
    with get_session() as db:
        exists = UserRepository(db).get_by_id(str(user_id)) is not None
    if not exists:
        raise ValidationError(f"User with ID {user_id} does not exist.")


def validate_item_id(item_id):
    with get_session() as db:
        exists = MenuItemRepository(db).get_by_id(str(item_id)) is not None
    if not exists:
        raise ValidationError(f"Item with ID {item_id} does not exist.")


def validate_size_id(size_id):
    with get_session() as db:
        exists = SizeRepository(db).get_by_id(str(size_id)) is not None
    if not exists:
        raise ValidationError(f"Size with ID {size_id} does not exist.")


def validate_vendor_id(vendor_id):
    with get_session() as db:
        exists = VendorRepository(db).get_by_id((str(vendor_id))) is not None
    if not exists:
        raise ValidationError(f"Vendor with ID {vendor_id} does not exist.")


def validate_webhook_id(webhook_id):
    with get_session() as db:
        exists = WebhookRepository(db).find_by_id(webhook_id) is not None
    if not exists:
        raise ValidationError(f"Webhook with ID {webhook_id} does not exist.")


def validate_menu_id(menu_id):
    with get_session() as db:
        exists = MenuRepository(db).get_by_id(menu_id) is not None
    if not exists:
        raise ValidationError(f"Menu with ID {menu_id} does not exist.")


class IDSchema(Schema):
    order_id = fields.Integer(validate=validate_order_id)
    user_id = fields.UUID(validate=validate_user_id)
    src_user_id = fields.UUID(validate=validate_user_id)
    vendor_id = fields.UUID(validate=validate_vendor_id)
    webhook_id = fields.UUID(validate=validate_webhook_id)
    item_id = fields.Integer(validate=validate_item_id)
    size_id = fields.Integer(validate=validate_size_id)
    menu_id = fields.Integer(validate=validate_menu_id)
    menu_date = fields.Date()
    notification_type = fields.Str(
        validate=validate.OneOf([nt.value for nt in NotificationType])
    )
