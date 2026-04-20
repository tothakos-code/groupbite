"""auto_migration

Revision ID: 7f1bee4584b3
Revises: 0d3d892b399e
Create Date: 2026-02-26 19:42:57.168660

"""

import json
import logging
from typing import Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "7f1bee4584b3"
down_revision = "0d3d892b399e"
branch_labels = None
depends_on = None

CURRENT_SCHEMA_VERSION = 1


def migrate_vendor_settings(raw: Union[dict, str]) -> dict:
    """Convert old metadata-object format to values-only format."""
    if isinstance(raw, str):
        raw = json.loads(raw)

    if not isinstance(raw, dict):
        return {"schemaVersion": CURRENT_SCHEMA_VERSION, "core": {}, "plugins": {}}

    if raw.get("schemaVersion") == CURRENT_SCHEMA_VERSION and "core" in raw:
        return raw

    core = {}
    for key, val in raw.items():
        if isinstance(val, dict) and "value" in val:
            core[key] = val["value"]
        else:
            logging.warning(
                "Unexpected settings shape for key %r: %r — storing as-is", key, val
            )
            core[key] = val

    return {
        "schemaVersion": CURRENT_SCHEMA_VERSION,
        "core": core,
        "plugins": {},
    }


def upgrade():
    conn = op.get_bind()
    rows = conn.execute(text("SELECT id, settings FROM vendor")).fetchall()

    migrated = 0
    skipped = 0

    for row in rows:
        vendor_id, raw_settings = row[0], row[1]

        if isinstance(raw_settings, str):
            raw_settings = json.loads(raw_settings)

        if (
            isinstance(raw_settings, dict)
            and raw_settings.get("schemaVersion") == CURRENT_SCHEMA_VERSION
            and "core" in raw_settings
        ):
            skipped += 1
            continue

        new_settings = migrate_vendor_settings(raw_settings)

        conn.execute(
            text("UPDATE vendor SET settings = cast(:s AS jsonb) WHERE id = :id"),
            {"s": json.dumps(new_settings), "id": str(vendor_id)},
        )
        migrated += 1

    logging.info(
        "Vendor settings migration complete: %d migrated, %d already up-to-date.",
        migrated,
        skipped,
    )


def downgrade():
    """
    Reverses the migration: unwraps core values back into metadata objects.
    Type info is reconstructed from the registry so the shape is correct,
    but any settings added after the upgrade that don't exist in the registry
    will be stored with type=UNKNOWN and a null section.
    """
    try:
        from app.utils.vendor_settings_registry import VendorSettingsRegistry

        registry = VendorSettingsRegistry.get_all()
    except ImportError:
        registry = {}

    conn = op.get_bind()
    rows = conn.execute(text("SELECT id, settings FROM vendor")).fetchall()

    for row in rows:
        vendor_id, raw_settings = row[0], row[1]

        if isinstance(raw_settings, str):
            raw_settings = json.loads(raw_settings)

        # Skip if already in old format (no schemaVersion key)
        if not isinstance(raw_settings, dict) or "core" not in raw_settings:
            continue

        core = raw_settings.get("core", {})
        old_format = {}

        for key, value in core.items():
            if key in registry:
                setting_def = registry[key]
                old_format[key] = {
                    "name": setting_def.labelKey,
                    "type": setting_def.get_type(),
                    "value": value,
                    "section": setting_def.section,
                }
            else:
                old_format[key] = {
                    "name": key,
                    "type": "UNKNOWN",
                    "value": value,
                    "section": "general",
                }

        conn.execute(
            text("UPDATE vendor SET settings = cast(:s AS jsonb) WHERE id = :id"),
            {"s": json.dumps(old_format), "id": str(vendor_id)},
        )
