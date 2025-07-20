from flask import Blueprint, request
import json
import logging

from app.entities.webhook import Webhook, WebhookType, BaseWebhookSchema, UpdateWebhookSchema
from app.controllers import webhook_blueprint
from app.utils.decorators import validate_data, validate_url_params, require_auth, require_admin
from app.utils.validators import IDSchema


@webhook_blueprint.route("/test", methods=["POST"])
@require_auth
@require_admin
def handle_webhook_test():
    try:
        data = request.json["data"]
        Webhook.validate_update_data(data)
        Webhook.send_to_google_chat(data["url"], data["message_template"])
    except Exception as e:
        logging.exception(e)
        return { "error": "Bad request" }, 400

    return { "msg": "OK", "data": data }, 200


@webhook_blueprint.route("/", methods=["POST"])
@validate_data(BaseWebhookSchema())
@require_auth
@require_admin
def handle_webhook_add(data):
    ok, webhook = Webhook.add(Webhook(
        vendor_id = data["vendor_id"],
        url = data["url"],
        message_template = data["message_template"],
        trigger_type = WebhookType(data["trigger_type"]),
        scheduled_time = data["scheduled_time"],
        event_types = data["event_types"],
        ))

    if not ok:
        return { "error": "Bad request" }, 400

    return { "msg": "OK", "data": webhook.serialized }, 201



@webhook_blueprint.route("/<webhook_id>", methods=["PUT"])
@validate_url_params(IDSchema())
@validate_data(UpdateWebhookSchema())
@require_auth
@require_admin
def handle_webhook_update(data, webhook_id):
    webhook = Webhook.find_by_id(webhook_id)

    if not webhook.update(
        url=data["url"],
        message_template=data["message_template"],
        trigger_type=WebhookType(data["trigger_type"]),
        scheduled_time=data["scheduled_time"],
        event_types=data["event_types"],
        is_active=data["is_active"]):
        return { "error": "Bad request" }, 400

    return { "msg": "OK" }, 200



@webhook_blueprint.route("/<webhook_id>", methods=["DELETE"])
@validate_url_params(IDSchema())
@require_auth
@require_admin
def handle_webhook_delete(webhook_id):
    if not Webhook.find_by_id(webhook_id).delete():
        return { "error": "IntegrityError" }, 400
    return { "msg": "OK" }, 204
