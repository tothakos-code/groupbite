from datetime import date
from os import getenv
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Blueprint, render_template, send_from_directory

from app.db.session import get_session
from app.services.vendor_service import VendorService
from app.socketio_singleton import SocketioSingleton

dotenv_path = Path(".env")
load_dotenv(dotenv_path=dotenv_path)
APP_ENV = getenv("APP_ENV")
VAPID_PUBLIC_KEY = getenv("VAPID_PUBLIC_KEY")

socketio = SocketioSingleton.get_instance()


class MainController:
    def __init__(self) -> None:
        self.blueprint = self._create_blueprint()
        self._register_routes()

    def _create_blueprint(self) -> Blueprint:
        return Blueprint(
            "main_controller",
            __name__,
            static_folder="../../frontend/dist",
            template_folder="../../frontend/dist",
        )

    def _register_routes(self):
        bp = self.blueprint
        bp.add_url_rule("/<path:path>", view_func=self.catch_all)
        bp.add_url_rule(
            "/vapid_public_key", view_func=self.get_vapid_public_key, methods=["GET"]
        )

    def catch_all(self, path):
        if path.startswith(("service-worker.js")):
            return send_from_directory(self.blueprint.static_folder, path)

        if APP_ENV == "development":
            # logging.debug("Redirecting to Frontned...")
            # This is for developer mode only
            return requests.get("http://127.0.0.1:8080/{0}".format(path)).text

        if path.startswith(("css/", "js/", "styles.css")):
            return send_from_directory(self.blueprint.static_folder, path)

        return render_template("index.html")

    def get_vapid_public_key(self):
        return VAPID_PUBLIC_KEY, 200


@socketio.on("connect")
def handle_connect(auth=None):
    with get_session() as db:
        socketio.emit(
            "be_vendors_update",
            [v.serialized for v in VendorService.find_all_active(db)],
        )
