from flask import Blueprint

from app.controllers.menu_controller import MenuController
from app.controllers.order_controller import OrderController
from app.controllers.size_controller import SizeController
from app.controllers.user_controller import UserController
from app.controllers.vendor_controller import VendorController
from app.controllers.webhook_controller import WebhookController
from app.event_manager import event_manager
from app.services.menu_service import MenuService
from app.services.order_service import OrderService
from app.services.size_service import SizeService
from app.services.user_basket_service import UserBasketService
from app.services.user_service import UserService
from app.services.vendor_service import VendorService
from app.services.webhook_service import WebhookService

main_blueprint = Blueprint("main_controller", __name__, static_folder="../../frontend/dist", template_folder="../../frontend/dist")
setting_blueprint = Blueprint("setting_controller", __name__, url_prefix="/api/setting")
item_blueprint = Blueprint("item_controller", __name__, url_prefix="/api/item")


def register_blueprints(app):
    user_basket_service = UserBasketService()
    menu_service = MenuService()
    order_service = OrderService(user_basket_service)
    size_service = SizeService()
    user_service = UserService(user_basket_service)
    vendor_service = VendorService(order_service)
    webhook_service = WebhookService(event_manager)

    menu_ctrl = MenuController(menu_service)
    order_ctrl = OrderController(order_service, user_basket_service)
    size_ctrl = SizeController(size_service)
    user_ctrl = UserController(user_service)
    vendor_ctrl = VendorController(vendor_service, webhook_service)
    webhook_ctrl = WebhookController(webhook_service)

    app.register_blueprint(menu_ctrl.blueprint)
    app.register_blueprint(order_ctrl.blueprint)
    app.register_blueprint(size_ctrl.blueprint)
    app.register_blueprint(user_ctrl.blueprint)
    app.register_blueprint(vendor_ctrl.blueprint)
    app.register_blueprint(webhook_ctrl.blueprint)

    # this registering all routes for the blueprint
    from .item_controller import item_blueprint
    from .main_controller import main_blueprint
    from .setting_controller import setting_blueprint

    # registering the blueprint in the app
    app.register_blueprint(main_blueprint)
    app.register_blueprint(setting_blueprint)
    app.register_blueprint(item_blueprint)
