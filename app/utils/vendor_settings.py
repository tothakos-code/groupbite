from __future__ import annotations

import copy
import logging
from typing import Any, Dict, Tuple

from sqlalchemy.orm.attributes import flag_modified

from app.utils.vendor_settings_registry import (
    CURRENT_SCHEMA_VERSION,
    VendorSettingsRegistry,
)

log = logging.getLogger(__name__)

_EMPTY_BLOB: Dict = {
    "schemaVersion": CURRENT_SCHEMA_VERSION,
    "core": {},
    "plugins": {},
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _ensure_shape(raw: Any) -> Dict:
    """Return a normalised blob regardless of what comes from the DB."""
    if not isinstance(raw, dict):
        return copy.deepcopy(_EMPTY_BLOB)
    blob = copy.deepcopy(raw)
    blob.setdefault("schemaVersion", CURRENT_SCHEMA_VERSION)
    blob.setdefault("core", {})
    blob.setdefault("plugins", {})
    return blob


def _merge_defaults(core: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
    """
    Merge registry defaults into *core* for any missing key.
    Returns (merged_core, was_anything_added).
    Pure function — does not touch the DB.
    """
    defaults = VendorSettingsRegistry.defaults()
    added = False
    merged = dict(defaults)  # start from defaults
    merged.update(core)  # overlay actual stored values
    if len(merged) > len(core):
        added = True
    return merged, added


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def load_vendor_settings(vendor) -> Dict[str, Any]:
    """
    Read vendor.settings from the ORM object, merge defaults in-memory,
    and return a fully-populated core dict.

    Does NOT persist anything.
    """
    blob = _ensure_shape(vendor.settings)
    core, _ = _merge_defaults(blob["core"])
    return core


def save_vendor_settings(
    vendor, patch: Dict[str, Any], db_session=None
) -> Dict[str, str]:
    """
    Validate and persist a patch of core settings.

    patch  — {key: value} of settings to update (values only, no metadata).
    Returns a dict of {key: error_message} for invalid keys; empty = success.
    Caller is responsible for db_session.commit().
    """
    errors: Dict[str, str] = {}

    for key, value in patch.items():
        if not VendorSettingsRegistry.get(key):
            errors[key] = "unknown_setting"
            continue
        if not VendorSettingsRegistry.validate_value(key, value):
            errors[key] = "invalid_value"
            log.warning("Invalid setting value for %s: %r", key, value)

    if errors:
        return errors

    blob = _ensure_shape(vendor.settings)
    blob["core"].update(patch)
    blob["schemaVersion"] = CURRENT_SCHEMA_VERSION

    vendor.settings = blob
    flag_modified(vendor, "settings")
    return {}


def get_setting_value(vendor, key: str, default: Any = None) -> Any:
    """Retrieve a single setting value, falling back to registry default."""
    blob = _ensure_shape(vendor.settings)
    core = blob["core"]
    if key in core:
        return core[key]
    setting_def = VendorSettingsRegistry.get(key)
    if setting_def:
        return setting_def.get_default_value()
    return default


def public_settings(vendor) -> Dict[str, Any]:
    """
    Return only public settings, suitable for unauthenticated / customer API.
    """
    core = load_vendor_settings(vendor)
    public_keys = VendorSettingsRegistry.public_keys()
    return {k: v for k, v in core.items() if k in public_keys}


def plugin_settings(vendor, plugin_id: str) -> Dict[str, Any]:
    """Return a copy of the settings blob for a specific plugin namespace."""
    blob = _ensure_shape(vendor.settings)
    return copy.deepcopy(blob["plugins"].get(plugin_id, {}))


def save_plugin_settings(vendor, plugin_id: str, patch: Dict[str, Any]) -> None:
    """Persist plugin-namespaced settings. No registry validation (plugins define their own)."""
    blob = _ensure_shape(vendor.settings)
    blob["plugins"].setdefault(plugin_id, {}).update(patch)
    blob["schemaVersion"] = CURRENT_SCHEMA_VERSION
    vendor.settings = blob
    flag_modified(vendor, "settings")
