from app.entities import Base, engine
from app.entities.user import User, Theme
from app.entities.menu import Menu, Frequency
from app.entities.order import Order, OrderState
from app.entities.vendor import Vendor, VendorType
from app.entities.menu_item import MenuItem
from app.entities.user_basket import UserBasket
from app.entities.setting import Setting
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

def migrate_database(app):
    """Automatically applies database migrations on startup."""
    with app.app_context():
        logging.info("Applying database migrations...")

        alembic_cfg = Config()
        alembic_cfg.set_main_option("script_location", "db/migrations")
        alembic_cfg.set_main_option("config_file_name", "alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", app.config["SQLALCHEMY_DATABASE_URI"])
        command.upgrade(alembic_cfg, "head")

        # upgrade(directory=migrations_dir)
        logging.info("Database migrations applied.")
