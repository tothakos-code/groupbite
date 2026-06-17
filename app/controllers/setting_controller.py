import re

from flask import Blueprint, request

from app.repositories.setting_repository import SettingRepository
from app.services.mail_sender_service import EmailService
from app.services.setting_service import SettingService
from app.utils.decorators import handle_request, require_admin, require_auth


class SettingController:
    def __init__(self, setting_service: SettingService) -> None:
        self.setting_service = setting_service
        self.blueprint = self._create_blueprint()
        self._register_routes()

    def _create_blueprint(self) -> Blueprint:
        return Blueprint("setting_controller", __name__, url_prefix="/api/setting")

    _PUBLIC_KEYS = frozenset({"app_title"})

    def _register_routes(self):
        bp = self.blueprint
        bp.add_url_rule("/get-all", view_func=self.get_all_settings, methods=["GET"])
        bp.add_url_rule("/get/<key>", view_func=self.get_setting, methods=["GET"])
        bp.add_url_rule("/public/<key>", view_func=self.get_public_setting, methods=["GET"])
        bp.add_url_rule("/set", view_func=self.update_setting, methods=["PUT"])
        bp.add_url_rule(
            "/mail/send-test", view_func=self.send_test_mail, methods=["POST"]
        )

    @require_auth
    @require_admin
    @handle_request
    def get_all_settings(self, db):
        return SettingRepository(db).get_all_settings_as_kv()

    @handle_request
    def get_public_setting(self, db, key):
        if key not in self._PUBLIC_KEYS:
            return {"error": "Not found"}, 404
        setting = self.setting_service.get_setting(db, key)
        return {setting.key: setting.value}

    @require_auth
    @handle_request
    def get_setting(self, db, key):
        setting = self.setting_service.get_setting(db, key)
        return {setting.key: setting.value}

    @require_auth
    @require_admin
    @handle_request
    def update_setting(self, db):
        data = request.json
        result = {"error": {}}
        for key, value in data.items():
            if not self.setting_service.update_setting(db, key, value):
                result["error"][key] = "Setting not found"
        if result["error"] == {}:
            return {"message": "Setting updated successfully"}
        return result, 404

    @require_auth
    @require_admin
    @handle_request
    def send_test_mail(self, db):
        test_email = request.json["test-email"]
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", test_email):
            raise ValueError("Not a valid email address.")

        email_service = EmailService()
        ok = email_service.send_test_mail([test_email], request.json)

        if not ok:
            raise Exception("Error during email sending")
        return {"message": "Mail sent"}, 200
