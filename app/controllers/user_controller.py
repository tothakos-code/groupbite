import logging
import re
from datetime import datetime, timedelta, timezone
from venv import logger

from flask import Blueprint, request, session

from app.repositories.user_repository import UserRepository
from app.services.mail_sender_service import EmailService
from app.services.user_service import UserService
from app.socketio_singleton import SocketioSingleton
from app.utils.decorators import (
    handle_request,
    require_admin,
    require_auth,
    validate_url_params,
)
from app.utils.validators import IDSchema

socketio = SocketioSingleton.get_instance()

COOLDOWN = timedelta(minutes=15)


class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service
        self.blueprint = self._create_blueprint()
        self._register_routes()

    def _create_blueprint(self) -> Blueprint:
        return Blueprint("user_controller", __name__, url_prefix="/api/user")

    def _register_routes(self):
        bp = self.blueprint
        bp.add_url_rule("/login", view_func=self.handle_user_login, methods=["POST"])
        bp.add_url_rule("/logout", view_func=self.handle_user_logout, methods=["POST"])
        bp.add_url_rule(
            "/checkSession", view_func=self.handle_user_check_session, methods=["GET"]
        )
        bp.add_url_rule("/reminder", view_func=self.handle_reminder, methods=["GET"])
        bp.add_url_rule(
            "/register", view_func=self.handle_user_register, methods=["POST"]
        )
        bp.add_url_rule(
            "/<user_id>", view_func=self.handle_user_update, methods=["PUT"]
        )
        bp.add_url_rule(
            "/<user_id>/orders",
            view_func=self.handle_user_order_history,
            methods=["GET"],
        )
        bp.add_url_rule("/", view_func=self.handle_get_users, methods=["GET"])
        bp.add_url_rule(
            "/<user_id>/statistics", view_func=self.user_statistics, methods=["GET"]
        )
        bp.add_url_rule(
            "/<user_id>/spending-trends",
            view_func=self.user_spending_trends,
            methods=["GET"],
        )
        bp.add_url_rule(
            "/<user_id>/vendor-breakdown",
            view_func=self.user_vendor_breakdown,
            methods=["GET"],
        )

    @handle_request
    def handle_user_login(self, db):
        user_id = session.get("user_id")
        user = self.user_service.login(db, user_id)
        return {"data": user.serialized}, 200

    @require_auth
    @handle_request
    def handle_user_logout(self, db):
        user_id = session.get("user_id")
        return self.user_service.logout(user_id)

    @handle_request
    def handle_user_check_session(self, db):
        user_id = session.get("user_id")
        user = self.user_service.check_session(db, user_id)
        return {"data": user.serialized}, 200

    @handle_request
    def handle_reminder(self, db):
        email = request.args.get("email")
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
            return {"error": "Helytelen email formátum"}, 200

        user = UserRepository(db).get_by_email(email)
        if user:
            now = datetime.now(timezone.utc)
            last = user.last_password_reset_at
            if last is not None and (now - last) < COOLDOWN:
                # dont send email to prevent spam
                return {"msg": "OK"}, 200

            email_service = EmailService()
            ok = email_service.send_username_reminder(user)

            if not ok:
                logging.error(
                    "Mail service not available, cannot send username reminder"
                )
                return {"msg": "Something went wrong"}, 500

            user.last_password_reset_at = now
        return {"msg": "OK"}, 200

    @handle_request
    def handle_user_register(self, db):
        username = request.json["username"]
        email = request.json["email"]
        user = self.user_service.register(db, email, username)
        return {"data": user.serialized}, 201

    @validate_url_params(IDSchema())
    @require_auth
    @handle_request
    def handle_user_update(self, db, user_id):
        user_data = request.json["data"]
        user = self.user_service.update_user(db, user_id, user_data)
        return {"data": user.serialized}, 200

    @validate_url_params(IDSchema())
    @handle_request
    def handle_user_order_history(self, db, user_id):
        orders = self.user_service.get_user_history(db, user_id, request.args)
        return {"data": orders}, 200

    @require_auth
    @require_admin
    @handle_request
    def handle_get_users(self, db):
        users = self.user_service.get_users(db, request.args)
        return {"data": users}

    @require_auth
    @handle_request
    def user_statistics(self, db, user_id):
        stats = self.user_service.get_user_statistics(db, user_id)
        return {"statistics": stats}

    @require_auth
    @handle_request
    def user_spending_trends(self, db, user_id):
        trends = self.user_service.get_user_spending_trends(db, user_id)
        return {"trends": trends}

    @require_auth
    @handle_request
    def user_vendor_breakdown(self, db, user_id):
        breakdown = self.user_service.get_user_vendor_breakdown(db, user_id)
        return {"breakdown": breakdown}
