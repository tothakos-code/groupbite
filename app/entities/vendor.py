from enum import Enum as pyenum
from sqlalchemy.dialects.postgresql import JSONB
from . import Base, session
from datetime import date
from sqlalchemy import Boolean, select, exc, event
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm.attributes import flag_modified
from uuid import UUID, uuid4
from typing import List
import logging
from typing import Any
from marshmallow import Schema, fields
from .notification import NotificationType
from app.entities.setting import Setting
from app.utils.vendor_settings_registry import VendorSettingsRegistry
import re

non_mached = re.compile("\$\{.*?\}")


class BaseVendorSchema(Schema):
    name = fields.Str(required=True)
    active = fields.Bool()
    settings = fields.Dict(required=True)

class VendorType(pyenum):
    PLUGIN = "plugin"
    BASIC = "basic"

    def __str__(self):
        return self.value

class Vendor(Base):
    __tablename__ = "vendor"

    id: Mapped[UUID] = mapped_column(primary_key=True, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean(), default=False)
    type: Mapped[VendorType] = mapped_column(default=VendorType.BASIC)
    settings: Mapped[dict] = mapped_column(JSONB)

    orders: Mapped[List["Order"]] = relationship(back_populates="vendor")

    def __repr__(self):
        return f"Vendor<id={self.id},name={self.name},type={str(self.type)}>"

    def _validate_settings(self):
        """Ensure all required settings exist with proper defaults"""
        if not isinstance(self.settings, dict):
            self.settings = {}

        # Get default settings from registry
        default_settings = VendorSettingsRegistry.get_default_settings_dict()

        # Merge with existing settings, keeping existing values
        for key, default_setting in default_settings.items():
            if key not in self.settings:
                self.settings[key] = default_setting
            else:
                # Ensure the structure is correct
                existing = self.settings[key]
                if not isinstance(existing, dict):
                    # Reset to default if structure is wrong
                    self.settings[key] = default_setting
                else:
                    # Ensure all required keys exist
                    for required_key in ["name", "type", "value", "section"]:
                        if required_key not in existing:
                            if required_key == "value":
                                existing[required_key] = default_setting[required_key]
                            else:
                                existing[required_key] = default_setting[required_key]

    def find_all():
        stmt = select(Vendor).order_by(Vendor.name)
        return session.execute(stmt).scalars().all()

    def find_all_by_type(type):
        stmt = select(Vendor).where(Vendor.type == type)
        return session.execute(stmt).scalars().all()

    def find_all_active():
        stmt = select(Vendor).where(Vendor.active == True)
        return session.execute(stmt).scalars().all()

    def find_by_id(id):
        stmt = select(Vendor).where(Vendor.id == id)
        return session.execute(stmt).scalars().first()

    def activate(self):
        self.active = True;
        session.commit()

    def deactivate(self):
        self.active = False;
        session.commit()

    def get_setting_value(self, key: str, default=None):
        """Safely get a setting value with fallback to default"""
        try:
            if key in self.settings and "value" in self.settings[key]:
                return self.settings[key]["value"]
        except (KeyError, TypeError):
            pass

        # Fallback to registry default
        setting_def = VendorSettingsRegistry.get_setting_by_key(key)
        if setting_def:
            return setting_def.get_default_value()

        return default

    def set_setting_value(self, key: str, value: Any) -> bool:
        """Safely set a setting value with validation"""
        if not VendorSettingsRegistry.validate_setting(key, value):
            return False

        if key not in self.settings:
            # Create from default if doesn't exist
            setting_def = VendorSettingsRegistry.get_setting_by_key(key)
            if setting_def:
                self.settings[key] = setting_def.to_dict()
            else:
                return False

        self.settings[key]["value"] = value
        flag_modified(self, "settings")
        return True

    def update_settings(self, settings):
        """Update multiple settings with proper validation and scheduling"""
        # Validate all settings first
        for key, setting_data in settings.items():
            if not isinstance(setting_data, dict) or "value" not in setting_data:
                continue
            if not VendorSettingsRegistry.validate_setting(key, setting_data["value"]):
                logging.warning(f"Invalid setting value for {key}: {setting_data['value']}")
                continue

        # Check for scheduler changes
        self._handle_scheduler_changes(settings)

        # Update settings
        self.settings = settings
        flag_modified(self, "settings")

        try:
            session.commit()
            return True
        except exc.DataError as e:
            logging.exception("DataError during vendor update")
            session.rollback()
            return False
        except Exception as e:
            logging.exception("Unhandled exception happened, rolling back")
            session.rollback()
            return False

    def _handle_scheduler_changes(self, new_settings):
        """Handle scheduler task updates when settings change"""
        # Closure scheduler
        closure_active_changed = (
            self.get_setting_value("closure_scheduler_active") !=
            new_settings.get("closure_scheduler_active", {}).get("value")
        )
        closure_time_changed = (
            self.get_setting_value("closure_scheduler") !=
            new_settings.get("closure_scheduler", {}).get("value")
        )

        if closure_active_changed or closure_time_changed:
            from app.scheduler import schedule_task, cancel_task
            cancel_task(str(self.id) + "-closure")

            if new_settings.get("closure_scheduler_active", {}).get("value"):
                time_value = new_settings.get("closure_scheduler", {}).get("value", "")
                if ":" in time_value:
                    hh, mm = time_value.split(":")
                    schedule_task(str(self.id) + "-closure", int(hh), int(mm), self.closure_wrapper)

        # Closed scheduler
        closed_active_changed = (
            self.get_setting_value("closed_scheduler_active") !=
            new_settings.get("closed_scheduler_active", {}).get("value")
        )
        closed_time_changed = (
            self.get_setting_value("closed_scheduler") !=
            new_settings.get("closed_scheduler", {}).get("value")
        )

        if closed_active_changed or closed_time_changed:
            from app.scheduler import schedule_task, cancel_task
            cancel_task(str(self.id) + "-closed")

            if new_settings.get("closed_scheduler_active", {}).get("value"):
                time_value = new_settings.get("closed_scheduler", {}).get("value", "")
                if ":" in time_value:
                    hh, mm = time_value.split(":")
                    schedule_task(str(self.id) + "-closed", int(hh), int(mm), self.closed_wrapper)

        # Auto email order scheduler
        auto_email_changed = (
            self.get_setting_value("auto_email_order") !=
            new_settings.get("auto_email_order", {}).get("value")
        )

        if new_settings.get("auto_email_order", {}).get("value") and Setting.get_value_by_key("smtp_address") != "":
            email_scheduler_changed = (
                self.get_setting_value("email_order_scheduler") !=
                new_settings.get("email_order_scheduler", {}).get("value")
            )

            if auto_email_changed or email_scheduler_changed:
                from app.scheduler import schedule_task, cancel_task
                cancel_task(str(self.id) + "-email-order")

                if new_settings.get("auto_email_order", {}).get("value"):
                    time_value = new_settings.get("email_order_scheduler", {}).get("value", "")
                    if ":" in time_value:
                        hh, mm = time_value.split(":")
                        schedule_task(str(self.id) + "-email-order", int(hh), int(mm), self.email_ordering_wrapper)
        else:
            logging.warning("No SMTP server set")
            # Revert to previous values if SMTP not configured
            if "auto_email_order" in new_settings:
                new_settings["auto_email_order"]["value"] = self.get_setting_value("auto_email_order")
            if "email_order_scheduler" in new_settings:
                new_settings["email_order_scheduler"]["value"] = self.get_setting_value("email_order_scheduler")


    def update_setting(self, key, value):
        """Update a single setting value"""
        if not VendorSettingsRegistry.validate_setting(key, value):
            return False

        if not self.set_setting_value(key, value):
            return False

        try:
            session.commit()
            return True
        except exc.DataError as e:
            logging.exception("DataError during vendor update")
            session.rollback()
            return False
        except Exception as e:
            logging.exception("Unhandled exception happened, rolling back")
            session.rollback()
            return False

    def add_vendor(vendor_obj):
        stmt = select(Vendor).where(Vendor.name == vendor_obj.name)
        vendor_db = session.execute(stmt).scalars().first()

        if not vendor_db:
            # insert
            vendor_id = uuid4()
            session.add(Vendor(id=vendor_id, name=vendor_obj.name, type=vendor_obj.type, settings=vendor_obj.settings))
            vendor_obj.id = str(vendor_id)
            logging.info("New Vendor registered in database: {0}".format(vendor_obj.name))
        else:
            vendor_obj.id = str(vendor_db.id)
            vendor_db._validate_settings()
            logging.info("Vendor already registered, loaded from database: {0}".format(vendor_obj.name))


            if vendor_db.get_setting_value("closure_scheduler_active"):
                from app.scheduler import schedule_task, cancel_task
                hh, mm = vendor_db.get_setting_value("closure_scheduler").split(":")
                schedule_task(str(vendor_db.id) + "-closure", int(hh), int(mm), vendor_db.closure_wrapper)

            if vendor_db.get_setting_value("closed_scheduler_active"):
                from app.scheduler import schedule_task, cancel_task
                hh, mm = vendor_db.get_setting_value("closed_scheduler").split(":")
                schedule_task(str(vendor_db.id) + "-closed", int(hh), int(mm), vendor_db.closed_wrapper)

            if vendor_db.get_setting_value("auto_email_order"):
                from app.scheduler import schedule_task, cancel_task
                hh, mm = vendor_db.get_setting_value("email_order_scheduler").split(":")
                schedule_task(str(vendor_db.id) + "-email-order", int(hh), int(mm), vendor_db.email_ordering_wrapper)


        try:
            session.commit()
            return True
        except exc.DataError as e:
            logging.exception("DataError during vendor update")
            session.rollback()
            return False
        except Exception as e:
            logging.exception("Unhadled exception happened, rolling back")
            session.rollback()
            return False

    def closure_wrapper(self):
        logging.info("Scheduled order state stepping running")
        from app.socketio_singleton import SocketioSingleton
        from app.entities.order import Order, OrderState
        from app.services.notification_service import NotificationService

        order = Order.find_open_order_by_date_for_a_vendor(self.id, date.today().strftime("%Y-%m-%d"))
        if order:
            ok = order.change_state(OrderState.ORDER, None)
            if not ok:
                logging.error("Error during order close")

            socketio = SocketioSingleton.get_instance()
            socketio.emit("be_order_update", {
                "order": order.serialized
            })
            NotificationService.send_vendor_notification(self, order, NotificationType.REMINDER)
        else:
            logging.info("State already changed")


    def closed_wrapper(self):
        logging.info("Scheduled order state stepping running")
        from app.entities.order import Order, OrderState

        order = Order.find_open_order_by_date_for_a_vendor(str(self.id), date.today().strftime("%Y-%m-%d"))
        if not order:
            logging.info("State already changed")
            return

        from app.socketio_singleton import SocketioSingleton
        order.change_state(OrderState.CLOSED, None)
        socketio = SocketioSingleton.get_instance()
        socketio.emit("be_order_update", {
            "order": order.serialized
        })


    def email_ordering_wrapper(self, order_id=None, manual=False):
        logging.info(("Manual" if manual else "Scheduled") + " email ordering running")
        from app.entities.order import Order, OrderState

        if not order_id:
            order = Order.find_order_by_date_for_a_vendor(str(self.id), date.today().strftime("%Y-%m-%d"))
        else:
            order = Order.get_by_id(order_id)

        if not order:
            logging.warning("Order not found")
            return False

        email_min_user = self.get_setting_value("email_min_user")
        if manual or (self.get_setting_value("auto_email_order") == True and (email_min_user == 0 or email_min_user <= len(order.get_users()))):
            from app.services.mail_sender_service import send_mail
            from app.entities.user_basket import UserBasket
            baskets = UserBasket.find_items_by_order(order.id)
            if len(baskets) == 0:
                logging.warning("The order is empty, email not sent")
                return False

            basket_sum = {}
            for item in baskets:
                if item.menu_item_id in basket_sum:
                    basket_sum[item.menu_item_id]["quantity"] += item.count
                else:
                    basket_sum[item.menu_item_id] = {**item.basket_format, "quantity": item.count}

            basket_template = ""
            basket_categories = {}
            for item in basket_sum.values():
                pattern = self.get_setting_value("order_text_template")
                line = pattern \
                    .replace("${quantity}", str(item["quantity"])) \
                    .replace("${item_name}", item["item_name"]) \
                    .replace("${size_name}", item["size_name"]) \
                    .replace("\\n", "<br>")
                basket_template += line

                if item["category"] not in basket_categories:
                    basket_categories[item["category"]] = ""
                basket_categories[item["category"]] += line

            email_template = self.get_setting_value("auto_email_order_template")
            email_template = email_template.replace("${basket}", basket_template)
            for category, value in basket_categories.items():
                email_template = email_template.replace("${basket." + category + "}", basket_categories[category])
            email_template = non_mached.sub("", email_template)

            email_subject = self.get_setting_value("auto_email_subject")
            email_subject = email_subject \
                .replace("${vendor_name}", order.vendor.name) \
                .replace("${date}", order.date_of_order.strftime("%Y.%m.%d"))

            email_subject = non_mached.sub("", email_subject)

            success, error = send_mail(
                self.get_setting_value("auto_email_order_to"),
                self.get_setting_value("auto_email_order_cc"),
                email_subject,
                email_template)
            if not success:
                logging.error("Email could not be sent")
                return False

            logging.info("Scheduled automatic order email sent!")

            if not order.change_state(OrderState.CLOSED):
                return True

            from app.socketio_singleton import SocketioSingleton
            socketio = SocketioSingleton.get_instance()

            socketio.emit("be_order_update", {
                "order": order.serialized
                },
                to=f"{order.vendor_id}@{order.date_of_order}"
            )
            return True
        else:
            logging.info("Minimum order requirements are not met")
            return False


    @property
    def serialized(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "active": self.active,
            "type": str(self.type),
            "settings": self.settings,
        }


def validate_before_save(mapper, connection, target):
    target._validate_settings()

event.listen(Vendor, "before_insert", validate_before_save)
event.listen(Vendor, "before_update", validate_before_save)
