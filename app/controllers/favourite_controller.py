import threading
from datetime import date

from flask import Blueprint, request, session

from app.services.favourite_service import FavouriteService
from app.utils.decorators import handle_request, require_auth, validate_url_params
from app.utils.validators import IDSchema


class FavouriteController:
    def __init__(self, favourite_service: FavouriteService):
        self.favourite_service = favourite_service
        self.blueprint = self._create_blueprint()
        self._register_routes()

    def _create_blueprint(self) -> Blueprint:
        return Blueprint("favourite_controller", __name__, url_prefix="/api/vendor")

    def _register_routes(self):
        bp = self.blueprint
        bp.add_url_rule(
            "/<vendor_id>/favourites",
            view_func=self.handle_get_favourites,
            methods=["GET"],
        )
        bp.add_url_rule(
            "/<vendor_id>/favourites",
            view_func=self.handle_add_favourite,
            methods=["POST"],
        )
        # matches must be registered before <favourite_id> to avoid route conflict
        bp.add_url_rule(
            "/<vendor_id>/favourites/matches",
            view_func=self.handle_get_matches,
            methods=["GET"],
        )
        bp.add_url_rule(
            "/<vendor_id>/favourites/<favourite_id>",
            view_func=self.handle_remove_favourite,
            methods=["DELETE"],
        )

    @require_auth
    @validate_url_params(IDSchema())
    @handle_request
    def handle_get_favourites(self, db, vendor_id):
        user_id = session.get("user_id")
        favourites = self.favourite_service.get_favourites(db, user_id, vendor_id)
        return {"data": [f.serialized for f in favourites]}, 200

    @require_auth
    @validate_url_params(IDSchema())
    @handle_request
    def handle_add_favourite(self, db, vendor_id):
        user_id = session.get("user_id")
        item_name = request.json.get("item_name")
        if not item_name:
            return {"error": "item_name required"}, 400
        favourite = self.favourite_service.add_favourite(db, user_id, vendor_id, item_name)
        db.commit()
        threading.Thread(
            target=self._notify_on_new_favourite,
            args=(user_id, vendor_id, item_name),
            daemon=True,
        ).start()
        return {"data": favourite.serialized}, 201

    @staticmethod
    def _notify_on_new_favourite(user_id, vendor_id, item_name):
        from app.db.session import get_session
        with get_session() as db:
            FavouriteService.notify_on_new_favourite(db, user_id, vendor_id, item_name)

    @require_auth
    @handle_request
    def handle_remove_favourite(self, db, vendor_id, favourite_id):
        user_id = session.get("user_id")
        self.favourite_service.remove_favourite(db, user_id, favourite_id)
        db.commit()
        return {"msg": "OK"}, 200

    @require_auth
    @validate_url_params(IDSchema())
    @handle_request
    def handle_get_matches(self, db, vendor_id):
        user_id = session.get("user_id")
        menu_date = request.args.get("date", str(date.today()))
        matches = self.favourite_service.get_matches_for_date(db, user_id, vendor_id, menu_date)
        return {"data": matches}, 200
