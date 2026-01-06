import importlib
import logging
from typing import Type

from app.entities.vendor import Vendor, VendorType
from app.repositories.vendor_repository import VendorRepository
from app.services.base_vendor_service import BaseVendorService
from app.services.vendor_service_factory import VendorServiceFactory


class ModuleInterface:
    @staticmethod
    def register() -> None:
        pass


def import_module(name: str) -> ModuleInterface:
    """Imports a module given a name."""
    return importlib.import_module(name)  # type: ignore


def load_plugins(db, plugin_dirs: list) -> None:
    for plugin_dir in plugin_dirs:
        logging.info(f"Importing plugins from {plugin_dir}")
        plugin_name = plugin_dir.name
        module_path = f"plugins.{plugin_name}.app"
        try:
            plugin_module = import_module(module_path)
            logging.info(f"Imported plugin module: {module_path}")
        except ModuleNotFoundError as e:
            logging.exception(
                f"{plugin_dir} plugin can not be imported, module not found: {e}"
            )
            continue

        service_class = _find_service_class(plugin_module)
        if not service_class:
            logging.error(f"No service class found in {module_path}")
            continue

        plugin_config = getattr(plugin_module, "PLUGIN_CONFIG", {})
        vendor_name = plugin_config.get("name", plugin_name)
        default_settings = plugin_config.get("default_settings", {})

        vendor_repo = VendorRepository(db)
        vendor = vendor_repo.get_by_name_and_type(vendor_name, VendorType.PLUGIN)

        if vendor:
            logging.info(
                f"Plugin vendor '{vendor_name}' already exists (id: {vendor.id})"
            )
        else:
            vendor = Vendor(
                name=vendor_name, type=VendorType.PLUGIN, settings=default_settings
            )
            vendor_repo.save(vendor)
            logging.info(f"Created new plugin vendor '{vendor_name}' (id: {vendor.id})")

        VendorServiceFactory.register_vendor_service(vendor, service_class)
        service_class.register()
        logging.info(
            f"Registered service {service_class.__name__} for vendor {vendor.id}"
        )

        # self._setup_vendor_automation(vendor)


def _find_service_class(module) -> Type[BaseVendorService]:
    for name, obj in module.__dict__.items():
        if (
            isinstance(obj, type)
            and issubclass(obj, BaseVendorService)
            and obj != BaseVendorService
        ):
            return obj
    return None
