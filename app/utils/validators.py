from app.entities.order import Order
from app.entities.user import User
from app.entities.menu_item import MenuItem
from app.entities.size import Size
from app.entities.vendor import Vendor
from app.entities.menu import Menu
from marshmallow import Schema, fields, ValidationError


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
    exists = Size.find_by_id(size_id) is not None
    if not exists:
        raise ValidationError(f"Size with ID {size_id} does not exist.")

def validate_vendor_id(vendor_id):
    exists = Vendor.find_by_id((str(vendor_id))) is not None
    if not exists:
        raise ValidationError(f"Vendor with ID {vendor_id} does not exist.")

def validate_menu_id(menu_id):
    exists = Menu.find_by_id(menu_id) is not None
    if not exists:
        raise ValidationError(f"Vendor with ID {menu_id} does not exist.")


class IDSchema(Schema):
    order_id = fields.Integer(validate=validate_order_id)
    user_id = fields.UUID(validate=validate_user_id)
    src_user_id = fields.UUID(validate=validate_user_id)
    vendor_id = fields.UUID(validate=validate_vendor_id)
    item_id = fields.Integer(validate=validate_item_id)
    size_id = fields.Integer(validate=validate_size_id)
    menu_id = fields.Integer(validate=validate_menu_id)
    menu_date = fields.Date()
