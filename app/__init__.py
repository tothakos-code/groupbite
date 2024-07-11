from flask import Flask
import logging

from app.services.vendor_service import VendorService
from app.vendor_factory import VendorFactory
import app.loader

from app.controllers import main_blueprint
from app.controllers import vendor_blueprint
from app.controllers import menu_blueprint
from app.controllers import order_blueprint
from app.controllers import user_blueprint

from dotenv import load_dotenv
from pathlib import Path
from os import getenv, scandir

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)
APP_HOST = getenv('APP_HOST')
APP_PORT = getenv('APP_PORT')

def create_app(debug=False):
    logging.basicConfig(
        level=logging.NOTSET,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )
    logging.info("Initialization started")

    application = Flask(__name__)
    application.config['SECRET_KEY'] = 'secret!'

    import app.create_tables

    VendorFactory.load()
    loader.load_plugins([d.path.replace('/','.') for d in scandir('plugins') if d.is_dir()])

    from app.socketio_singleton import SocketioSingleton
    socketio = SocketioSingleton.get_instance()
    socketio.init_app(
        application,
        host=APP_HOST,
        port=APP_PORT,
        debug=debug,
        async_mode='eventlet',
        allow_unsafe_werkzeug=True)

    import app.controllers.main_controller
    application.register_blueprint(main_blueprint)
    import app.controllers.vendor_controller
    application.register_blueprint(vendor_blueprint)
    import app.controllers.menu_controller
    application.register_blueprint(menu_blueprint)
    import app.controllers.order_controller
    application.register_blueprint(order_blueprint)
    import app.controllers.user_controller
    application.register_blueprint(user_blueprint)

    logging.info("Initialization finished")
    return application
