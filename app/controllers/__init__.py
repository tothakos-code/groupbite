from flask import Blueprint
from flask_restful import Api

main_blueprint = Blueprint("main_controller", __name__, static_folder="../../frontend/dist", template_folder="../../frontend/dist")
setting_blueprint = Blueprint("setting_controller", __name__, url_prefix="/api/setting")
vendor_blueprint = Blueprint("vendor_controller", __name__, url_prefix="/api/vendor")
menu_blueprint = Blueprint("menu_controller", __name__, url_prefix="/api/menu")
order_blueprint = Blueprint("order_controller", __name__, url_prefix="/api/order")
user_blueprint = Blueprint("user_controller", __name__, url_prefix="/api/user")
