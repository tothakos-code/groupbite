from flask import Blueprint
from flask_restful import Api

main_blueprint = Blueprint("main_controller", __name__, static_folder="../../frontend/dist", template_folder="../../frontend/dist")
setting_blueprint = Blueprint("setting_controller", __name__, url_prefix="/api/setting")
vendor_blueprint = Blueprint("vendor_controller", __name__, url_prefix="/api/vendor")
menu_blueprint = Blueprint("menu_controller", __name__, url_prefix="/api/menu")
item_blueprint = Blueprint("item_controller", __name__, url_prefix="/api/item")
size_blueprint = Blueprint("size_controller", __name__, url_prefix="/api/size")
order_blueprint = Blueprint("order_controller", __name__, url_prefix="/api/order")
user_blueprint = Blueprint("user_controller", __name__, url_prefix="/api/user")


def register_blueprints(app):
    # this registering all routes for the blueprint
    from .main_controller import main_blueprint
    from .setting_controller import setting_blueprint
    from .vendor_controller import vendor_blueprint
    from .menu_controller import menu_blueprint
    from .item_controller import item_blueprint
    from .size_controller import size_blueprint
    from .order_controller import order_blueprint
    from .user_controller import user_blueprint

    # registering the blueprint in the app
    app.register_blueprint(main_blueprint)
    app.register_blueprint(setting_blueprint)
    app.register_blueprint(vendor_blueprint)
    app.register_blueprint(menu_blueprint)
    app.register_blueprint(item_blueprint)
    app.register_blueprint(size_blueprint)
    app.register_blueprint(order_blueprint)
    app.register_blueprint(user_blueprint)
