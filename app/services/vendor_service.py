import json
import logging
from configparser import ParsingError
from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified

from app.entities.menu import Menu
from app.entities.menu_item import MenuItem
from app.entities.notification import NotificationType
from app.entities.setting import Setting
from app.entities.size import Size
from app.entities.vendor import Vendor, VendorType
from app.repositories.menu_repository import MenuRepository
from app.repositories.vendor_repository import VendorRepository
from app.services.base_vendor_service import BaseVendorService
from app.services.vendor_service_factory import VendorServiceFactory
from app.utils.vendor_settings_registry import VendorSettingsRegistry


class MenuItemRepository:
    pass


class VendorService:
    def __init__(self):
        pass

    @staticmethod
    def scan_menu(db, vendor_id, menu_date=None):
        service = VendorServiceFactory.get_service(db, vendor_id)
        service.scan(db, menu_date=menu_date)

    @staticmethod
    def get_menu_items(db, vendor_id, date, filter=None):
        if filter is None:
            filter = []

        menus = MenuRepository(db).find_active_by_vendor_id(vendor_id, date)
        result = []

        for menu in menus:
            items = MenuItem.find_all_by_menu_list([menu.id], filter, limit=100)

            categorized_items = {}
            for item in items:
                category = item.category or "egyéb"
                if category not in categorized_items:
                    categorized_items[category] = []
                categorized_items[category].append(item.serialized)

            result_items = []
            for category in sorted(categorized_items.keys(), key=lambda x: x.lower()):
                result_items.extend(categorized_items[category])

            result.append(
                {
                    "menu_id": menu.id,
                    "from_date": str(menu.from_date),
                    "to_date": str(menu.to_date),
                    "items": result_items,
                    "total_items": len(result_items),
                    "categories": list(categorized_items.keys()),
                }
            )

        return result

    @staticmethod
    def get_menus(db, vendor_id, args):
        try:
            limit = int(args.get("limit"))
            page = int(args.get("page"))
        except ValueError:
            limit = 10
            page = 1
        except TypeError:
            limit = 10
            page = 1
        search = args.get("search")
        active = args.get("active")
        date_from = args.get("date_from")
        date_to = args.get("date_to")

        offset = 0 if page is None else limit * (page - 1)
        menus = Menu.find_by_vendor(
            vendor_id, limit, offset, search, active, date_from, date_to
        )
        all_menus = Menu.find_by_vendor(
            vendor_id, None, 0, search, active, date_from, date_to
        )

        total_count = len(all_menus)
        result = [m.serialized for m in menus]
        return {
            "menus": result,
            "page": page,
            "limit": limit,
            "total_count": total_count,
        }

    @staticmethod
    def get_vendor(db, vendor_id):
        vendor_repo = VendorRepository(db)
        return vendor_repo.get_by_id(vendor_id)

    @staticmethod
    def get_vendors(db):
        vendor_repo = VendorRepository(db)
        return vendor_repo.find_all()

    @staticmethod
    def activate_vendor(db, vendor_id):
        vendor_repo = VendorRepository(db)
        vendor = vendor_repo.get_by_id(vendor_id)
        vendor_repo.activate(vendor)
        logging.info("Vendor " + vendor.name + " got activated")
        return vendor

    @staticmethod
    def deactivate_vendor(db, vendor_id):
        vendor_repo = VendorRepository(db)
        vendor = vendor_repo.get_by_id(vendor_id)
        vendor_repo.deactivate(vendor)
        logging.info("Vendor " + vendor.name + " got deactivated")
        return vendor

    @staticmethod
    def find_all_active(db):
        vendor_repo = VendorRepository(db)
        return vendor_repo.find_all_active()

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

    def set_setting_value(self, key: str, value: any) -> bool:
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
                logging.warning(
                    f"Invalid setting value for {key}: {setting_data['value']}"
                )
                continue

        # Check for scheduler changes
        self._handle_scheduler_changes(settings)

        # Update settings
        self.settings = settings
        flag_modified(self, "settings")

    def _handle_scheduler_changes(self, new_settings):
        """Handle scheduler task updates when settings change"""
        # Closure scheduler
        closure_active_changed = self.get_setting_value(
            "closure_scheduler_active"
        ) != new_settings.get("closure_scheduler_active", {}).get("value")
        closure_time_changed = self.get_setting_value(
            "closure_scheduler"
        ) != new_settings.get("closure_scheduler", {}).get(
            "value"
        ) or self.get_setting_value("closure_scheduler_days") != new_settings.get(
            "closure_scheduler_days", {}
        ).get("value")

        if closure_active_changed or closure_time_changed:
            from app.scheduler import cancel_task, schedule_task

            cancel_task(str(self.id) + "-closure")

            if new_settings.get("closure_scheduler_active", {}).get("value"):
                time_value = new_settings.get("closure_scheduler", {}).get("value", "")
                if ":" in time_value:
                    hh, mm = time_value.split(":")
                    schedule_task(
                        str(self.id) + "-closure",
                        int(hh),
                        int(mm),
                        self.closure_wrapper,
                        new_settings.get("closure_scheduler_days", {}).get("value"),
                    )

        # Closed scheduler
        closed_active_changed = self.get_setting_value(
            "closed_scheduler_active"
        ) != new_settings.get("closed_scheduler_active", {}).get("value")
        closed_time_changed = self.get_setting_value(
            "closed_scheduler"
        ) != new_settings.get("closed_scheduler", {}).get(
            "value"
        ) or self.get_setting_value("closed_scheduler_days") != new_settings.get(
            "closed_scheduler_days", {}
        ).get("value")

        if closed_active_changed or closed_time_changed:
            from app.scheduler import cancel_task, schedule_task

            cancel_task(str(self.id) + "-closed")

            if new_settings.get("closed_scheduler_active", {}).get("value"):
                time_value = new_settings.get("closed_scheduler", {}).get("value", "")
                if ":" in time_value:
                    hh, mm = time_value.split(":")
                    schedule_task(
                        str(self.id) + "-closed",
                        int(hh),
                        int(mm),
                        self.closed_wrapper,
                        new_settings.get("closed_scheduler_days", {}).get("value"),
                    )

        # Auto email order scheduler
        auto_email_changed = self.get_setting_value(
            "auto_email_order"
        ) != new_settings.get("auto_email_order", {}).get("value")

        if (
            new_settings.get("auto_email_order", {}).get("value")
            and Setting.get_value_by_key("smtp_address") == ""
        ):
            logging.warning("No SMTP server set")
            # Revert to previous values if SMTP not configured
            if "auto_email_order" in new_settings:
                new_settings["auto_email_order"]["value"] = self.get_setting_value(
                    "auto_email_order"
                )

    def update_setting(self, key, value):
        if not VendorSettingsRegistry.validate_setting(key, value):
            return False

        if not self.set_setting_value(key, value):
            return False

    @staticmethod
    def create_vendor(db, data) -> Vendor:
        vendor = Vendor(
            id=uuid4(),
            name=data["name"],
            type=VendorType.BASIC,
            settings=data.get("settings", {}),
        )
        # Todo: Vendor factory review
        vendor = VendorRepository(db).save(vendor)
        vendor._validate_settings()
        VendorServiceFactory.register_vendor_service(vendor, BaseVendorService)

        if vendor.get_setting_value("closure_scheduler_active"):
            from app.scheduler import cancel_task, schedule_task

            hh, mm = vendor.get_setting_value("closure_scheduler").split(":")
            schedule_task(
                str(vendor.id) + "-closure", int(hh), int(mm), vendor.closure_wrapper
            )

        if vendor.get_setting_value("closed_scheduler_active"):
            from app.scheduler import cancel_task, schedule_task

            hh, mm = vendor.get_setting_value("closed_scheduler").split(":")
            schedule_task(
                str(vendor.id) + "-closed", int(hh), int(mm), vendor.closed_wrapper
            )
        return vendor

    @staticmethod
    def import_menu(db, vendor_id, files) -> None:
        if "file" not in files:
            raise ValueError("No file part in the request")

        json_file = files["file"]

        if json_file.filename == "":
            raise ValueError("No file selected for uploading")

        try:
            file_content = json.loads(json_file.read())
            for menu in file_content["menus"]:
                menu_db = Menu(
                    name=menu["name"]
                    if "name" in menu
                    else "imported-" + datetime.now().strftime("%Y-%m-%d-%H:%M"),
                    vendor_id=vendor_id,
                    from_date=menu["from_date"]
                    if "from_date" in menu
                    else date.today().strftime("%Y-%m-%d"),
                    to_date=menu["to_date"]
                    if "to_date" in menu
                    else date.today().strftime("%Y-%m-%d"),
                )

                item_index = 0
                for item in menu["items"]:
                    menu_item = MenuItem(
                        name=item["name"],
                        category=item["category"] if "category" in item else "",
                        index=item["index"] if "index" in item else item_index,
                    )
                    if "index" not in item:
                        item_index += 1

                    size_index = 0
                    for size in item["sizes"]:
                        menu_item.sizes.append(
                            Size(
                                link="",
                                name=size["name"],
                                price=size["price"],
                                index=size["index"] if "index" in size else size_index,
                                quantity=size["quantity"] if "quantity" in size else -1,
                                unlimited=size["unlimited"]
                                if "unlimited" in size
                                else True,
                            )
                        )
                        if "index" not in size:
                            size_index += 1

                    menu_db.items.append(menu_item)
                Menu.add(menu_db)

        except Exception as e:
            raise ValueError("Failed to parse JSON file", e)

    def closure_wrapper(self):
        logging.info("Scheduled order 'ORDER' state stepping running")
        from app.entities.order import Order, OrderState
        from app.event_manager import event_manager
        from app.services.notification_service import NotificationService
        from app.socketio_singleton import SocketioSingleton

        order = Order.find_open_order_by_date_for_a_vendor(
            self.id, date.today().strftime("%Y-%m-%d")
        )
        if not order:
            logging.info("Open order not found for state changing")
            return
        event_manager.trigger_event("beforeOrder@" + self.name, {"order_id": order.id})

        ok = order.change_state(OrderState.ORDER, None)
        if not ok:
            logging.error("Error during order close")

        socketio = SocketioSingleton.get_instance()
        socketio.emit("be_order_update", {"order": order.serialized})
        NotificationService.send_vendor_notification(
            self, order, NotificationType.REMINDER
        )
        event_manager.trigger_event("afterOrder@" + self.name, {"order_id": order.id})

    def closed_wrapper(self):
        logging.info("Scheduled order 'CLOSED' state stepping running")
        from app.entities.order import Order, OrderState
        from app.event_manager import event_manager

        order = Order.find_open_order_by_date_for_a_vendor(
            str(self.id), date.today().strftime("%Y-%m-%d")
        )
        if not order:
            logging.info("Open order not found for state changing")
            return
        event_manager.trigger_event("beforeClose@" + self.name, {"order_id": order.id})

        from app.socketio_singleton import SocketioSingleton

        if self.get_setting_value("auto_email_order"):
            email_min_user = self.get_setting_value("email_min_user")
            if self.get_setting_value("auto_email_order") == True and (
                email_min_user == 0 or email_min_user <= len(order.get_users())
            ):
                logging.info("Scheduled email ordering running")
                email_sent = order.send_in_mail()
                if email_sent:
                    order.change_state(OrderState.CLOSED)
                else:
                    logging.info("There was an error sending the email.")
                    return False
            else:
                logging.info("Minimum order requirements are not met")
                event_manager.trigger_event(
                    "closeFailed@" + order.vendor.name, {"order_id": order.id}
                )
                return False
        else:
            order.change_state(OrderState.CLOSED, None)

        event_manager.trigger_event("afterClose@" + self.name, {"order_id": order.id})
        socketio = SocketioSingleton.get_instance()
        socketio.emit(
            "be_order_update",
            {"order": order.serialized},
            to=f"{order.vendor_id}@{order.date_of_order}",
        )

    def email_ordering_wrapper(self, order_id=None, manual=False):
        logging.info("Manual email ordering running")
        from app.entities.order import Order, OrderState
        from app.event_manager import event_manager

        if not order_id:
            order = Order.find_order_by_date_for_a_vendor(
                str(self.id), date.today().strftime("%Y-%m-%d")
            )
        else:
            order = Order.get_by_id(order_id)

        if not order:
            logging.warning("Order not found")
            return False

        event_manager.trigger_event(
            "beforeClose@" + order.vendor.name, {"order_id": order.id}
        )
        email_min_user = self.get_setting_value("email_min_user")
        if manual or (
            self.get_setting_value("auto_email_order") == True
            and (email_min_user == 0 or email_min_user <= len(order.get_users()))
        ):
            email_sent = order.send_in_mail()
            if email_sent:
                if not order.change_state(OrderState.CLOSED):
                    return True
                event_manager.trigger_event(
                    "afterClose@" + order.vendor.name, {"order_id": order.id}
                )

                from app.socketio_singleton import SocketioSingleton

                socketio = SocketioSingleton.get_instance()

                socketio.emit(
                    "be_order_update",
                    {"order": order.serialized},
                    to=f"{order.vendor_id}@{order.date_of_order}",
                )
                return True
            else:
                return False
        else:
            logging.info("Minimum order requirements are not met")
            event_manager.trigger_event(
                "closeFailed@" + order.vendor.name, {"order_id": order.id}
            )
            return False
