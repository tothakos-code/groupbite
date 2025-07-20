from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import timedelta

from app.services.vendor_service import VendorService
from app.services.webhook_service import webhook_service
from app.vendor_factory import VendorFactory
import app.loader

from app.controllers import main_blueprint
from app.controllers import setting_blueprint
from app.controllers import vendor_blueprint
from app.controllers import menu_blueprint
from app.controllers import item_blueprint
from app.controllers import size_blueprint
from app.controllers import order_blueprint
from app.controllers import user_blueprint
from app.controllers import statistics_blueprint

from os import scandir, makedirs, path
import sys

from dotenv import load_dotenv
from pathlib import Path
from os import getenv
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
    logging.basicConfig(
        handlers=[handler],
        level=logging.NOTSET
    )

        # Redirect stdout and stderr to logger
    class LoggerWriter:
        def __init__(self, level):
            self.level = level
        def write(self, message):
            if message.strip():  # Avoid writing empty lines
                self.level(message)
        def flush(self):
            pass  # Needed for compatibility with sys.stdout/sys.stderr

    sys.stdout = LoggerWriter(logging.info)  # Redirect stdout (prints)
    sys.stderr = LoggerWriter(logging.error)

def create_migration():
    initialize_logging()
    application = Flask(__name__)
    application.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
    application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    from app.create_tables import create_database_migration
    create_database_migration(application)

def create_app(debug=False):
    initialize_logging()
    logging.info("Initialization started")

    application = Flask(__name__)
    application.config["SECRET_KEY"] = "secret!"
    application.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
    application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    application.config["SESSION_TYPE"] = "sqlalchemy"
    application.config["SESSION_SQLALCHEMY"] = SQLAlchemy(application)
    application.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=336)

    application.config['SESSION_COOKIE_HTTPONLY'] = True
    # application.config['SESSION_COOKIE_SECURE'] = True
    application.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    from app.create_tables import migrate_database
    migrate_database(application)
    Session(application)


    VendorFactory.load()
    loader.load_plugins([d.path.replace("/",".") for d in scandir("plugins") if d.is_dir()])

    from app.socketio_singleton import SocketioSingleton
    socketio = SocketioSingleton.get_instance()
    socketio.init_app(
        application,
        debug=debug,
        async_mode="eventlet",
        allow_unsafe_werkzeug=True)

    from app.controllers import register_blueprints

    register_blueprints(application)

    webhook_service.register_all_webhooks_at_boot()


    logging.info("Initialization finished")
    return application
