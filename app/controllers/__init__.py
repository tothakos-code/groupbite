from flask import Blueprint

from app.controllers.favourite_controller import FavouriteController
from app.controllers.item_controller import MenuItemController
from app.controllers.plugins_controller import PluginsController
from app.controllers.main_controller import MainController
from app.controllers.menu_controller import MenuController
from app.controllers.order_controller import OrderController
from app.controllers.setting_controller import SettingController
from app.controllers.size_controller import SizeController
from app.controllers.user_controller import UserController
from app.controllers.vendor_controller import VendorController
from app.controllers.webhook_controller import WebhookController
from app.event_manager import event_manager
from app.services.favourite_service import FavouriteService
from app.services.menu_item_service import MenuItemService
from app.services.menu_service import MenuService
from app.services.order_service import OrderService
from app.services.setting_service import SettingService
from app.services.size_service import SizeService
from app.services.user_basket_service import UserBasketService
from app.services.user_service import UserService
from app.services.vendor_service import VendorService
from app.services.webhook_service import WebhookService

statistics_blueprint = Blueprint(
    "statistics_controller", __name__, url_prefix="/api/statistics"
)


def register_blueprints(app):
    user_basket_service = UserBasketService()
    menu_item_service = MenuItemService()
    menu_service = MenuService()
    order_service = OrderService(user_basket_service)
    size_service = SizeService()
    user_service = UserService(user_basket_service)
    vendor_service = VendorService(order_service)
    setting_service = SettingService(vendor_service)
    webhook_service = WebhookService(event_manager)
    favourite_service = FavouriteService()

    menu_item_ctrl = MenuItemController(menu_item_service)
    menu_ctrl = MenuController(menu_service)
    order_ctrl = OrderController(order_service, user_basket_service)
    size_ctrl = SizeController(size_service)
    user_ctrl = UserController(user_service)
    vendor_ctrl = VendorController(vendor_service, webhook_service)
    setting_ctrl = SettingController(setting_service)
    webhook_ctrl = WebhookController(webhook_service)
    favourite_ctrl = FavouriteController(favourite_service)
    plugins_ctrl = PluginsController()
    main_ctrl = MainController()

    app.register_blueprint(menu_item_ctrl.blueprint)
    app.register_blueprint(menu_ctrl.blueprint)
    app.register_blueprint(order_ctrl.blueprint)
    app.register_blueprint(size_ctrl.blueprint)
    app.register_blueprint(user_ctrl.blueprint)
    app.register_blueprint(vendor_ctrl.blueprint)
    app.register_blueprint(setting_ctrl.blueprint)
    app.register_blueprint(webhook_ctrl.blueprint)
    app.register_blueprint(favourite_ctrl.blueprint)
    app.register_blueprint(plugins_ctrl.blueprint)
    app.register_blueprint(main_ctrl.blueprint)
