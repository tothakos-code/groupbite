import importlib
import logging
from app.vendor_factory import VendorFactory
from app.entities.vendor import VendorType
from app.base_vendor import BaseVendor

class ModuleInterface:

    @staticmethod
    def register() -> None:
        pass

def import_module(name: str) -> ModuleInterface:
    """Imports a module given a name."""
    return importlib.import_module(name)  # type: ignore


def load_plugins(plugins: list) -> None:
    """Loads the plugins defined in the plugins list."""
    for plugin_file in plugins:
        try:
            plugin = import_module(plugin_file+".app")
        except ModuleNotFoundError as e:
            logging.exception(f"{plugin_file} plugin can not be imported, module not found: ")
            continue


        for name, obj in plugin.__dict__.items():
            if isinstance(obj, type) and issubclass(obj, BaseVendor) and obj != BaseVendor:
                vendor_obj = obj()
                vendor_obj.type = VendorType.PLUGIN
                VendorFactory.register(vendor_obj)
                logging.info("Loaded {0} plugin".format(plugin.__name__))
