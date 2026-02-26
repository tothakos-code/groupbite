from flask import Blueprint, request

from app.entities.webhook import (
    BaseWebhookSchema,
    UpdateWebhookSchema,
)
from app.services.webhook_service import WebhookService
from app.utils.decorators import (
    handle_request,
    require_admin,
    require_auth,
    validate_data,
    validate_url_params,
)
from app.utils.validators import IDSchema


class WebhookController:
    def __init__(self, webhook_service: WebhookService):
        self.webhook_service = webhook_service
        self.blueprint = self._create_blueprint()
        self._register_routes()

    def _create_blueprint(self) -> Blueprint:
        return Blueprint("webhook_controller", __name__, url_prefix="/api/webhook")

    def _register_routes(self):
        bp = self.blueprint
        bp.add_url_rule(
            "/<webhook_id>", view_func=self.handle_webhook_delete, methods=["DELETE"]
        )
        bp.add_url_rule(
            "/<webhook_id>", view_func=self.handle_webhook_update, methods=["PUT"]
        )
        bp.add_url_rule("/", view_func=self.handle_webhook_add, methods=["POST"])
        bp.add_url_rule("/test", view_func=self.handle_webhook_test, methods=["POST"])

    @require_auth
    @require_admin
    @handle_request
    def handle_webhook_test(self, db):
        data = request.json["data"]
        self.webhook_service.test_webhook(data)
        return {"msg": "OK", "data": data}, 200

    @require_auth
    @require_admin
    @validate_data(BaseWebhookSchema())
    @handle_request
    def handle_webhook_add(self, db, data):
        webhook = self.webhook_service.add_webhook(db, data)
        return {"msg": "OK", "data": webhook.serialized}, 201

    @require_auth
    @require_admin
    @validate_url_params(IDSchema())
    @validate_data(UpdateWebhookSchema())
    @handle_request
    def handle_webhook_update(self, db, data, webhook_id):
        webhook = self.webhook_service.find_by_id(db, webhook_id)
        webhook = self.webhook_service.update_webhook(db, webhook, data)
        return {"msg": "OK"}, 200

    @require_auth
    @require_admin
    @validate_url_params(IDSchema())
    @handle_request
    def handle_webhook_delete(self, db, webhook_id):
        webhook = self.webhook_service.find_by_id(db, webhook_id)
        self.webhook_service.delete_webhook(db, webhook)
        return {"msg": "OK"}, 204
