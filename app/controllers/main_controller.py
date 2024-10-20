from datetime import date
from flask import Blueprint, request, send_from_directory, render_template, session
import logging
import requests

from app.controllers import main_blueprint
from app.socketio_singleton import SocketioSingleton
from app.services.vendor_service import VendorService



from dotenv import load_dotenv
from pathlib import Path
from os import getenv

dotenv_path = Path(".env")
load_dotenv(dotenv_path=dotenv_path)
APP_ENV = getenv("APP_ENV")
VAPID_PUBLIC_KEY = getenv("VAPID_PUBLIC_KEY")

socketio = SocketioSingleton.get_instance()

@main_blueprint.route("/", defaults={"path": ""})
@main_blueprint.route("/<path:path>")
def catch_all(path):

    if path.startswith(("service-worker.js")):
        return send_from_directory(main_blueprint.static_folder, path)

    if APP_ENV == "development":
        logging.info("Redirecting to Frontned...")
        # This is for developer mode only
        return requests.get("http://127.0.0.1:8080/{0}".format(path)).text

    if path.startswith(("css/", "js/", "styles.css")):
        return send_from_directory(main_blueprint.static_folder, path)

    return render_template("index.html")


@main_blueprint.route("/cron/new_day_refresh")
def cron_new_day_refresh():
    socketio.emit("Refresh!")
    return "Refreshed", 200

@main_blueprint.route("/vapid_public_key")
def get_vapid_public_key():
    return VAPID_PUBLIC_KEY, 200

@socketio.on("connect")
def handle_connect(auth=None):
    socketio.emit("be_vendors_update", VendorService.find_all_active())
    pass
