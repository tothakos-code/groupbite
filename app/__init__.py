from flask import Flask
import logging


from app.controllers import main_blueprint
from app.controllers import menu_blueprint
from app.controllers import order_blueprint
from app.controllers import user_blueprint



def create_app(debug=False):
    logging.basicConfig(
        level=logging.NOTSET,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )
    logging.info("Initialization started")

    application = Flask(__name__)
    application.config['SECRET_KEY'] = 'secret!'
    import app.controllers.menu_controller
    application.register_blueprint(menu_blueprint)
    import app.controllers.order_controller
    application.register_blueprint(order_blueprint)
    import app.controllers.user_controller
    application.register_blueprint(user_blueprint)

    logging.info("Initialization finished")
    return application
