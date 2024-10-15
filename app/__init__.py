from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import logging
from datetime import timedelta

from app.services.vendor_service import VendorService
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

from os import scandir

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


def create_app(debug=False):
    logging.basicConfig(
        level=logging.NOTSET,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )
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
    Session(application)

    import app.create_tables

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

    logging.info("Initialization finished")
    return application
