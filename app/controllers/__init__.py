from flask import Blueprint
from flask_restful import Api

main_blueprint = Blueprint('main_controller', __name__)
# main_controller_api = Api(main_controller_bp)
menu_blueprint = Blueprint('menu_controller', __name__, url_prefix='/api/menu')
order_blueprint = Blueprint('order_controller', __name__, url_prefix='/api/order')
user_blueprint = Blueprint('user_controller', __name__, url_prefix='/api/user')
