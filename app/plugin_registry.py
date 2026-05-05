from typing import Dict, List, Optional, Type


class PluginRegistry:
    """Maps plugin_id -> BaseVendorService subclass and its settings schema."""

    _plugins: Dict[str, "Type"] = {}
    _plugin_settings: Dict[str, List] = {}

    @classmethod
    def register(cls, plugin_id: str, service_class: "Type") -> None:
        cls._plugins[plugin_id] = service_class

    @classmethod
    def get(cls, plugin_id: str) -> Optional["Type"]:
        return cls._plugins.get(plugin_id)

    @classmethod
    def all(cls) -> Dict[str, "Type"]:
        return dict(cls._plugins)

    @classmethod
    def register_settings(cls, plugin_id: str, settings: List) -> None:
        cls._plugin_settings[plugin_id] = settings

    @classmethod
    def get_settings(cls, plugin_id: str) -> List:
        return cls._plugin_settings.get(plugin_id, [])
