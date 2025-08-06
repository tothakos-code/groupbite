from flask import Blueprint, request
import json
import logging

from app.entities.menu_item import MenuItem, BaseItemSchema, UpdateItemSchema, BulkUpdateItemSchema
from app.entities.menu import Menu
from app.controllers import item_blueprint
from app.utils.decorators import validate_data, validate_url_params, require_auth, require_admin
from app.utils.validators import IDSchema


@item_blueprint.route("", methods=["POST"])
@validate_data(BaseItemSchema())
@require_auth
@require_admin
def handle_menu_item_add(data):
    if not Menu.find_by_id(data["menu_id"]):
        logging.warning("Menu not found")
        return {"error": "Menu not found"}, 400

    ok, item = MenuItem.add(MenuItem(
        menu_id  = data["menu_id"],
        name     = data["name"],
        description     = data["description"],
        category = data["category"]))

    if not ok:
        return { "error": "Bad request" }, 400

    return { "msg": "OK", "data": item.serialized }, 201


@item_blueprint.route("/<item_id>", methods=["PUT"])
@validate_url_params(IDSchema())
@validate_data(UpdateItemSchema())
@require_auth
@require_admin
def handle_menu_item_update(data, item_id):
    menu_item = MenuItem.find_by_id(item_id)

    if not menu_item.update(
        data["menu_id"],
        data["name"],
        data["description"],
        data["index"],
        data["category"]):
        return { "error": "Bad request" }, 400

    return { "msg": "OK" }, 200


@item_blueprint.route("/<item_id>", methods=["DELETE"])
@validate_url_params(IDSchema())
@require_auth
@require_admin
def handle_menu_item_delete(item_id):
    if not MenuItem.find_by_id(item_id).delete():
        return { "error": "IntegrityError" }, 400
    return { "msg": "OK" }, 200


@item_blueprint.route("/reorder", methods=["PUT"])
@validate_data(BulkUpdateItemSchema())
@require_auth
@require_admin
def handle_bulk_update_indices(data):
    """
    Bulk update menu item indices.
    Expects a list of items with id and new index values.
    """
    try:
        items_to_update = data["items"]

        # Extract item IDs for validation
        item_ids = [item["id"] for item in items_to_update]

        # Validate that all items are in the same menu:
        if MenuItem.count_unique_menu_ids_by_item_ids(item_ids) != 1:
            return {"error": f"Not all items are in the same menu"}, 400

        # Fetch all items that need to be updated
        menu_items = MenuItem.get_by_ids(item_ids)

        # Validate that all items exist
        if len(menu_items) != len(item_ids):
            found_ids = {item.id for item in menu_items}
            missing_ids = set(item_ids) - found_ids
            return {"error": f"Items not found: {list(missing_ids)}"}, 404

        # Update indices in bulk
        success = MenuItem.bulk_update_indices(items_to_update)

        if not success:
            return {"error": "Failed to update item indices"}, 500

        return {"msg": "Indices updated successfully", "updated_count": len(items_to_update)}, 200

    except Exception as e:
        logging.exception("Error during bulk index update")
        return {"error": "Internal server error"}, 500
