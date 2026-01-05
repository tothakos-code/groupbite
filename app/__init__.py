import logging
import sys
import time
from datetime import timedelta
from logging.handlers import TimedRotatingFileHandler
from os import getenv, makedirs, path, scandir
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, g, request
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

from app.config import Config
from app.controllers import (
    item_blueprint,
    main_blueprint,
    setting_blueprint,
    size_blueprint,
    statistics_blueprint,
)
from app.db.session import get_session, init_db
from app.event_manager import event_manager
from app.services.webhook_service import WebhookService

dotenv_path = Path(".env")
load_dotenv(dotenv_path=dotenv_path)

DB_USER = getenv("POSTGRES_USER")
DB_PASSWORD = getenv("POSTGRES_PASSWORD")
DB_HOST = getenv("POSTGRES_HOST")
DB_PORT = getenv("POSTGRES_PORT")
DB_NAME = getenv("POSTGRES_DB_NAME")

DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

LOG_FILE = "logs/groupbite.log"


def initialize_logging():
    makedirs(path.dirname(LOG_FILE), exist_ok=True)
    handler = TimedRotatingFileHandler(
        LOG_FILE, when="midnight", interval=1, backupCount=31, encoding="utf-8"
    )
    formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
    handler.setFormatter(formatter)
    logging.basicConfig(handlers=[handler], level=logging.NOTSET)

    class LoggerWriter:
        def __init__(self, level):
            self.level = level

        def write(self, message):
            if message.strip():
                self.level(message)

        def flush(self):
            pass

    sys.stdout = LoggerWriter(logging.info)
    sys.stderr = LoggerWriter(logging.error)


def create_migration():
    initialize_logging()
    application = Flask(__name__)
    application.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
    application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    from app.create_tables import create_database_migration

    create_database_migration(application)


def create_app(config: Config = Config(), debug=False) -> Flask:
    initialize_logging()
    logging.info("Initialization started")

    application = Flask(__name__)

    @application.before_request
    def _start_timer():
        g._start_time = time.perf_counter()

    @application.after_request
    def _log_request(response):
        # duration
        duration_ms = None
        if hasattr(g, "_start_time"):
            duration_ms = (time.perf_counter() - g._start_time) * 1000

        # useful request info
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        method = request.method
        full_path = request.full_path if request.query_string else request.path
        status = response.status_code
        ua = request.headers.get("User-Agent", "-")

        application.logger.info(
            'ip=%s method=%s path="%s" status=%s duration_ms=%.2f ua="%s"',
            ip,
            method,
            full_path,
            status,
            duration_ms or -1.0,
            ua,
        )
        return response

    application.config["SECRET_KEY"] = "secret!"
    application.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
    application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    application.config["SESSION_TYPE"] = "sqlalchemy"
    application.config["SESSION_SQLALCHEMY"] = SQLAlchemy(application)
    application.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=336)

    application.config["SESSION_COOKIE_HTTPONLY"] = True
    # application.config['SESSION_COOKIE_SECURE'] = True
    application.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    from app.create_tables import migrate_database

    migrate_database(application)
    Session(application)

    from app.socketio_singleton import SocketioSingleton

    socketio = SocketioSingleton.get_instance()
    socketio.init_app(
        application, debug=debug, async_mode="eventlet", allow_unsafe_werkzeug=True
    )

    # Initialize database
    init_db(application, config)
    with get_session() as db:
        loader.load_plugins(db, [d for d in scandir("plugins") if d.is_dir()])

        from app.controllers import register_blueprints

        register_blueprints(application)

        WebhookService(event_manager).register_all_webhooks_at_boot(db)

    logging.info("Initialization finished")
    return application
