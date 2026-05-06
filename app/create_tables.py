from app.entities import Base, engine
from app.entities.category import Category
from app.entities.user import User, Theme
from app.entities.menu import Menu, Frequency
from app.entities.order import Order, OrderState
from app.entities.order_item import OrderItem
from app.entities.notification import Notification, NotificationType
from app.entities.vendor import Vendor, MenuType
from app.entities.menu_item import MenuItem
from app.entities.user_basket import UserBasket
from app.entities.setting import Setting
from app.entities.webhook import Webhook, WebhookType
from app.entities.user_favourite import UserFavourite
from app.entities.option_group import OptionGroup, option_group_item
from app.entities.option_choice import OptionChoice
from app.entities.basket_option_selection import BasketOptionSelection
from app.entities.bundle_discount import BundleDiscount
from app.entities.bundle_slot import BundleSlot
from sqlalchemy import event
from flask_migrate import upgrade, migrate, stamp
import logging
import os
from alembic.config import Config
from alembic import command


def create_database_migration(app):
    """Genarating an auto migration with Alembic"""
    with app.app_context():
        logging.info("Applying database migrations...")
        alembic_cfg = Config()
        alembic_cfg.set_main_option("script_location", "db/migrations")
        alembic_cfg.set_main_option("config_file_name", "alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", app.config["SQLALCHEMY_DATABASE_URI"])
        command.revision(alembic_cfg, message="auto_migration", autogenerate=True)

def downgrade_database_migration(app, revision: str = "-1", plugin: str = None):
    """Downgrade the database by the given revision (default: one step back).
    Pass plugin=<name> to downgrade a plugin migration branch instead of the main app."""
    with app.app_context():
        db_url = app.config["SQLALCHEMY_DATABASE_URI"]
        if plugin:
            migrations_dir = os.path.join("plugins", plugin, "migrations")
            if not os.path.isdir(migrations_dir):
                raise ValueError(f"No migrations directory found for plugin '{plugin}'")
            logging.info(f"Downgrading plugin '{plugin}' to revision: {revision}...")
            alembic_cfg = Config()
            alembic_cfg.set_main_option("script_location", migrations_dir)
            alembic_cfg.set_main_option("sqlalchemy.url", db_url)
            alembic_cfg.set_main_option("version_table", "alembic_version_plugins")
        else:
            logging.info(f"Downgrading main app to revision: {revision}...")
            alembic_cfg = Config()
            alembic_cfg.set_main_option("script_location", "db/migrations")
            alembic_cfg.set_main_option("sqlalchemy.url", db_url)
        command.downgrade(alembic_cfg, revision)
        logging.info("Downgrade complete.")


def migrate_database(app):
    """Automatically applies database migrations on startup."""
    with app.app_context():
        logging.info("Applying database migrations...")

        db_url = app.config["SQLALCHEMY_DATABASE_URI"]

        main_cfg = Config()
        main_cfg.set_main_option("script_location", "db/migrations")
        main_cfg.set_main_option("sqlalchemy.url", db_url)
        command.upgrade(main_cfg, "head")

        if os.path.isdir("plugins"):
            for plugin in os.scandir("plugins"):
                if not plugin.is_dir():
                    continue
                migrations_dir = os.path.join(plugin.path, "migrations")
                if not os.path.isdir(os.path.join(migrations_dir, "versions")):
                    continue
                logging.info("Applying plugin migrations for: %s", plugin.name)
                plugin_cfg = Config()
                plugin_cfg.set_main_option("script_location", migrations_dir)
                plugin_cfg.set_main_option("sqlalchemy.url", db_url)
                plugin_cfg.set_main_option("version_table", "alembic_version_plugins")
                command.upgrade(plugin_cfg, "head")

        logging.info("Database migrations applied.")
