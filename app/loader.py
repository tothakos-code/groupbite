import importlib
import logging
from typing import Type

from app.plugin_registry import PluginRegistry
from app.repositories.vendor_repository import VendorRepository
from app.services.base_vendor_service import BaseVendorService


def load_plugins(db, plugin_dirs: list) -> None:
    vendor_repo = VendorRepository(db)

    for plugin_dir in plugin_dirs:
        plugin_name = plugin_dir.name
        module_path = f"plugins.{plugin_name}.app"

        try:
            plugin_module = importlib.import_module(module_path)
            logging.info(f"Imported plugin module: {module_path}")
        except ModuleNotFoundError as e:
            logging.exception(f"{plugin_dir} plugin cannot be imported: {e}")
            continue

        service_class = _find_service_class(plugin_module)
        if not service_class:
            logging.error(f"No service class found in {module_path}")
            continue

        plugin_config = getattr(plugin_module, "PLUGIN_CONFIG", {})
        plugin_id = plugin_config.get("id", plugin_name)

        plugin_settings = getattr(plugin_module, "PLUGIN_SETTINGS", [])
        if plugin_settings:
            PluginRegistry.register_settings(plugin_id, plugin_settings)

        PluginRegistry.register(plugin_id, service_class)

        vendor_ids = [str(v.id) for v in vendor_repo.get_by_plugin_id(plugin_id)]
        service_class.register(plugin_id, vendor_ids)

        logging.info(
            f"Registered plugin '{plugin_id}' ({service_class.__name__}) "
            f"for {len(vendor_ids)} vendor(s)"
        )


def _find_service_class(module) -> Type[BaseVendorService]:
    for name, obj in module.__dict__.items():
        if (
            isinstance(obj, type)
            and issubclass(obj, BaseVendorService)
            and obj is not BaseVendorService
        ):
            return obj
    return None
