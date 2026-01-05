from app.entities.order import Order
from app.entities.user import User
from marshmallow import Schema, ValidationError, fields, validate
from app.db.session import get_session
from app.entities.menu_item import MenuItem
from app.entities.size import Size
from app.entities.vendor import Vendor
from app.entities.webhook import Webhook
from app.entities.menu import Menu
from app.entities.notification import NotificationType
from marshmallow import Schema, fields, ValidationError, validate
from app.repositories.vendor_repository import VendorRepository


def validate_order_id(order_id):
    exists = Order.get_by_id(order_id) is not None
    if not exists:
        raise ValidationError(f"Order with ID {order_id} does not exist.")

def validate_user_id(user_id):
    exists = User.get_one_by_id(str(user_id)) is not None
    if not exists:
        raise ValidationError(f"User with ID {user_id} does not exist.")

def validate_item_id(item_id):
    exists = MenuItem.find_by_id(item_id) is not None
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
    exists = Menu.find_by_id(menu_id) is not None
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
    notification_type = fields.Str(validate=validate.OneOf([nt.value for nt in NotificationType]))
