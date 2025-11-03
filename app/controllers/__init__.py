from flask import Blueprint
from app.controllers.order_controller import OrderController
from app.services.order_service import OrderService
from app.repositories.order_item_repository import OrderItemRepository




main_blueprint = Blueprint("main_controller", __name__, static_folder="../../frontend/dist", template_folder="../../frontend/dist")
setting_blueprint = Blueprint("setting_controller", __name__, url_prefix="/api/setting")
vendor_blueprint = Blueprint("vendor_controller", __name__, url_prefix="/api/vendor")
menu_blueprint = Blueprint("menu_controller", __name__, url_prefix="/api/menu")
item_blueprint = Blueprint("item_controller", __name__, url_prefix="/api/item")
size_blueprint = Blueprint("size_controller", __name__, url_prefix="/api/size")
user_blueprint = Blueprint("user_controller", __name__, url_prefix="/api/user")
webhook_blueprint = Blueprint("webhook_controller", __name__, url_prefix="/api/webhook")
statistics_blueprint = Blueprint("statistics_controller", __name__, url_prefix="/api/statistics")


def register_blueprints(app):
    order_item_repository = OrderItemRepository()
    order_service = OrderService(order_item_repository)
    order_ctrl = OrderController(order_service)
    app.register_blueprint(order_ctrl.blueprint)

    # this registering all routes for the blueprint
    from .main_controller import main_blueprint
    from .setting_controller import setting_blueprint
    from .vendor_controller import vendor_blueprint
    from .menu_controller import menu_blueprint
    from .item_controller import item_blueprint
    from .size_controller import size_blueprint
    from .user_controller import user_blueprint
    from .webhook_controller import webhook_blueprint
    from .statistics_controller import statistics_blueprint

    # registering the blueprint in the app
    app.register_blueprint(main_blueprint)
    app.register_blueprint(setting_blueprint)
    app.register_blueprint(vendor_blueprint)
    app.register_blueprint(menu_blueprint)
    app.register_blueprint(item_blueprint)
    app.register_blueprint(size_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(webhook_blueprint)
    app.register_blueprint(statistics_blueprint)
