from os import getenv
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Blueprint, Response, render_template, request, send_from_directory

from app.db.session import get_session
from app.services.vendor_service import VendorService
from app.socketio_singleton import SocketioSingleton

dotenv_path = Path(".env")
load_dotenv(dotenv_path=dotenv_path)
APP_ENV = getenv("APP_ENV")
VAPID_PUBLIC_KEY = getenv("VAPID_PUBLIC_KEY")
FRONTEND_DEV_URL = getenv("FRONTEND_DEV_URL", "http://127.0.0.1:8080")

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
        bp.add_url_rule("/", view_func=self.catch_all)
        bp.add_url_rule("/<path:path>", view_func=self.catch_all)
        bp.add_url_rule(
            "/vapid_public_key", view_func=self.get_vapid_public_key, methods=["GET"]
        )

    def catch_all(self, path=""):
        if path.startswith("service-worker.js"):
            return send_from_directory(self.blueprint.static_folder, path)

        if APP_ENV == "development":
            upstream_url = f"{FRONTEND_DEV_URL}/{path}"
            r = requests.get(
                upstream_url,
                params=request.args,
                stream=True,
            )

            headers = {}
            for h in ("Content-Type", "Cache-Control", "ETag", "Last-Modified"):
                if h in r.headers:
                    headers[h] = r.headers[h]

            return Response(r.content, status=r.status_code, headers=headers)

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
