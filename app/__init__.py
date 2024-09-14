from flask import Flask
import logging

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


def create_app(debug=False):
    logging.basicConfig(
        level=logging.NOTSET,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )
    logging.info("Initialization started")

    application = Flask(__name__)
    application.config["SECRET_KEY"] = "secret!"

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
