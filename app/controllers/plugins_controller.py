from flask import Blueprint

from app.plugin_registry import PluginRegistry
from app.utils.decorators import handle_request, require_admin, require_auth


class PluginsController:
    def __init__(self):
        self.blueprint = self._create_blueprint()
        self._register_routes()

    def _create_blueprint(self) -> Blueprint:
        return Blueprint("plugins_controller", __name__, url_prefix="/api/plugins")

    def _register_routes(self):
        self.blueprint.add_url_rule(
            "", view_func=self.handle_get_plugins, methods=["GET"]
        )

    @require_auth
    @require_admin
    @handle_request
    def handle_get_plugins(self, db):
        plugins = [{"id": plugin_id} for plugin_id in PluginRegistry.all()]
        return {"data": plugins}, 200
