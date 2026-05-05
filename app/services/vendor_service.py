import json
import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Callable
from uuid import uuid4

from app.db.session import get_session
from app.entities.menu import Menu
from app.entities.menu_item import MenuItem
from app.entities.notification import NotificationType
from app.entities.size import Size
from app.entities.vendor import MenuType, Vendor
from app.repositories.menu_item_repository import MenuItemRepository
from app.repositories.menu_repository import MenuRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.setting_repository import SettingRepository
from app.repositories.vendor_repository import VendorRepository
from app.services.order_service import OrderService
from app.services.vendor_service_factory import VendorServiceFactory
from app.utils.vendor_settings import (
    get_setting_value,
    save_vendor_settings,
)


@dataclass
class _SchedulerSpec:
    task_id_suffix: str
    active_key: str
    time_key: str
    days_key: str
    callback: Callable


class VendorService:
    def __init__(self, order_service: OrderService):
        self.order_service = order_service

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
            items = MenuItemRepository(db).find_all_by_menu_list(
                [menu.id], filter, limit=100
            )

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
        menu_repo = MenuRepository(db)
        menus = menu_repo.find_by_vendor(
            vendor_id, limit, offset, search, active, date_from, date_to
        )
        all_menus = menu_repo.find_by_vendor(
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

    @staticmethod
    def get_setting_value(vendor, key: str, default=None):
        return get_setting_value(vendor, key, default)

    def set_setting_value(self, vendor, key: str, value) -> bool:
        errors = save_vendor_settings(vendor, {key: value})
        return len(errors) == 0

    def update_settings(self, vendor, settings: dict):
        normalised = {}
        for key, v in settings.items():
            if isinstance(v, dict) and "value" in v:
                normalised[key] = v["value"]
            else:
                normalised[key] = v

        self._handle_scheduler_changes(vendor, normalised)
        errors = save_vendor_settings(vendor, normalised)
        if errors:
            import logging

            logging.getLogger(__name__).warning(
                "Settings validation errors: %s", errors
            )
        return errors

    def update_setting(self, vendor, key, value) -> bool:
        return self.set_setting_value(vendor, key, value)

    def _handle_scheduler_changes(self, vendor, new_settings: dict):
        from app.scheduler import cancel_task, schedule_task

        specs = [
            _SchedulerSpec(
                "closure",
                "closure_scheduler_active",
                "closure_scheduler",
                "closure_scheduler_days",
                self.closure_wrapper,
            ),
            _SchedulerSpec(
                "closed",
                "closed_scheduler_active",
                "closed_scheduler",
                "closed_scheduler_days",
                self.closed_wrapper,
            ),
            _SchedulerSpec(
                "scan",
                "menu_scan_active",
                "menu_scan_time",
                "menu_scan_days",
                self.scan_wrapper,
            ),
            _SchedulerSpec(
                "favourite-notification",
                "favourite_notification_active",
                "favourite_notification_time",
                "favourite_notification_days",
                self.favourite_notification_wrapper,
            ),
        ]

        for spec in specs:
            self._sync_scheduler(vendor, new_settings, spec, cancel_task, schedule_task)

        self._handle_auto_email_guard(vendor, new_settings)

    def _sync_scheduler(
        self,
        vendor,
        new_settings: dict,
        spec: _SchedulerSpec,
        cancel_task,
        schedule_task,
    ):
        old_active = self.get_setting_value(vendor, spec.active_key)
        old_time = self.get_setting_value(vendor, spec.time_key)
        old_days = self.get_setting_value(vendor, spec.days_key)

        new_active = new_settings.get(spec.active_key, old_active)
        new_time = new_settings.get(spec.time_key, old_time)
        new_days = new_settings.get(spec.days_key, old_days)

        changed = (
            (old_active != new_active)
            or (old_time != new_time)
            or (old_days != new_days)
        )
        if not changed:
            return

        task_id = f"{vendor.id}-{spec.task_id_suffix}"
        cancel_task(task_id)

        if new_active and isinstance(new_time, str) and ":" in new_time:
            try:
                hh, mm = new_time.split(":")
                schedule_task(
                    task_id, int(hh), int(mm), spec.callback, new_days, vendor=vendor
                )
            except ValueError:
                logging.warning(
                    "Invalid time format for %s: %r", spec.time_key, new_time
                )

    def _handle_auto_email_guard(self, vendor, new_settings: dict):
        old_active = self.get_setting_value(vendor, "auto_email_order")
        new_active = new_settings.get("auto_email_order", old_active)

        if not new_active or new_active == old_active:
            return

        with get_session() as db:
            smtp_set = SettingRepository(db).get_value_by_key("smtp_address")

        if not smtp_set:
            logging.warning(
                "Vendor %s: auto_email_order enabled but no SMTP server configured — reverting.",
                vendor.id,
            )
            new_settings["auto_email_order"] = old_active

    def create_vendor(self, db, data) -> Vendor:
        from app.plugin_registry import PluginRegistry

        plugin_id = data.get("plugin_id") or None
        if plugin_id and not PluginRegistry.get(plugin_id):
            raise ValueError(f"Unknown plugin: {plugin_id}")

        menu_type = MenuType(data.get("menu_type", MenuType.FIXED_MENU.value))

        if VendorRepository(db).get_by_name(data["name"]):
            raise ValueError("name_taken")

        vendor = Vendor(
            id=uuid4(),
            name=data["name"],
            menu_type=menu_type,
            plugin_id=plugin_id,
            settings=data.get("settings", {}),
        )
        VendorRepository(db).save(vendor)
        vendor._validate_settings()

        if plugin_id:
            service_class = PluginRegistry.get(plugin_id)
            service_class.register(plugin_id, [str(vendor.id)])

        if self.get_setting_value(vendor, "closure_scheduler_active"):
            from app.scheduler import schedule_task

            hh, mm = self.get_setting_value(vendor, "closure_scheduler").split(":")
            schedule_task(
                str(vendor.id) + "-closure",
                int(hh),
                int(mm),
                self.closure_wrapper,
                vendor=vendor,
            )

        if self.get_setting_value(vendor, "closed_scheduler_active"):
            from app.scheduler import schedule_task

            hh, mm = self.get_setting_value(vendor, "closed_scheduler").split(":")
            schedule_task(
                str(vendor.id) + "-closed",
                int(hh),
                int(mm),
                self.closed_wrapper,
                vendor=vendor,
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
            from app.services.category_service import CategoryService

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
                    category = CategoryService.get_or_create(
                        db, vendor_id, item.get("category", "")
                    )
                    menu_item = MenuItem(
                        name=item["name"],
                        category_id=category.id,
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
                MenuRepository(db).save(menu_db)

        except Exception as e:
            raise ValueError("Failed to parse JSON file", e)

    def closed_wrapper(self, vendor):
        logging.info("Scheduled order 'CLOSED' state stepping running")
        from app.entities.order import OrderState
        from app.event_manager import event_manager

        with get_session() as db:
            order = self.order_service.find_open_order_by_vendor(
                db, vendor.id, date.today()
            )
            if not order:
                logging.info("Open order not found for state changing")
                return
            event_manager.trigger_event(
                "beforeClose@" + str(vendor.id),
                {"order_id": order.id, "order": order.serialized},
            )

            from app.socketio_singleton import SocketioSingleton

            if self.get_setting_value(vendor, "auto_email_order"):
                email_min_user = self.get_setting_value(vendor, "email_min_user")
                order_user_count = len(
                    OrderRepository(db).find_order_participants(order)
                )
                if self.get_setting_value(vendor, "auto_email_order") and (
                    email_min_user == 0 or email_min_user <= order_user_count
                ):
                    logging.info("Scheduled email ordering running")

                    self.order_service._change_state(db, order, OrderState.CLOSED)
                    self.order_service.send_in_mail(order)
                else:
                    logging.info("Minimum order requirements are not met")
                    event_manager.trigger_event(
                        "closeFailed@" + str(vendor.id),
                        {"order_id": order.id, "order": order.serialized},
                    )
                    return False
            else:
                self.order_service._change_state(db, order, OrderState.CLOSED)

            event_manager.trigger_event(
                "afterClose@" + str(vendor.id),
                {"order_id": order.id, "order": order.serialized},
            )
            socketio = SocketioSingleton.get_instance()
            socketio.emit(
                "be_order_update",
                {"order": order.serialized},
                to=f"{order.vendor_id}@{order.date_of_order}",
            )

    def closure_wrapper(self, vendor):
        logging.info("Scheduled order 'ORDER' state stepping running")
        from app.entities.order import OrderState
        from app.event_manager import event_manager
        from app.services.notification_service import NotificationService
        from app.socketio_singleton import SocketioSingleton

        with get_session() as db:
            order = self.order_service.find_open_order_by_vendor(
                db, vendor.id, date.today()
            )
            if not order:
                logging.info("Open order not found for state changing")
                return
            event_manager.trigger_event(
                "beforeOrder@" + str(vendor.id),
                {"order_id": order.id, "order": order.serialized},
            )
            ok = self.order_service._change_state(db, order, OrderState.ORDER)
            if not ok:
                logging.error("Error during order close")

            socketio = SocketioSingleton.get_instance()
            socketio.emit("be_order_update", {"order": order.serialized})
            include_favourite = bool(self.get_setting_value(vendor, "favourite_notification_on_order"))
            NotificationService.send_order_notifications(db, vendor, order, include_favourite)
            event_manager.trigger_event(
                "afterOrder@" + str(vendor.id),
                {"order_id": order.id, "order": order.serialized},
            )

    def favourite_notification_wrapper(self, vendor):
        logging.info("Scheduled favourite notification running")
        from app.services.favourite_service import FavouriteService

        with get_session() as db:
            FavouriteService.send_favourite_notifications(db, vendor)

    def scan_wrapper(self, vendor):
        logging.info("Scheduled menu scan running")
        from app.event_manager import event_manager

        days_ahead = self.get_setting_value(vendor, "menu_scan_days_ahead") or 1

        with get_session() as db:
            event_manager.trigger_event(
                "beforeScan@" + str(vendor.id),
                {"vendor_id": vendor.id, "vendor": vendor.serialized},
            )

            service = VendorServiceFactory.get_service(db, vendor.id)
            for day_offset in range(1, days_ahead + 1):
                scan_date = (date.today() + timedelta(days=day_offset)).strftime(
                    "%Y-%m-%d"
                )
                logging.info("Scanning menu for %s (day +%d)", scan_date, day_offset)
                service.scan(db, menu_date=scan_date)

            event_manager.trigger_event(
                "afterScan@" + str(vendor.id),
                {"vendor_id": vendor.id, "vendor": vendor.serialized},
            )

    @staticmethod
    def get_plugin_settings(db, vendor_id):
        from app.plugin_registry import PluginRegistry
        from app.utils.vendor_settings import plugin_settings as load_plugin_settings

        vendor = VendorRepository(db).get_by_id(vendor_id)
        if not vendor or not vendor.plugin_id:
            return None

        schema = PluginRegistry.get_settings(vendor.plugin_id)
        stored = load_plugin_settings(vendor, vendor.plugin_id)

        settings = {
            s.key: {**s.to_registry_dict(), "value": stored.get(s.key, s.get_default_value())}
            for s in schema
        }
        return {"plugin_id": vendor.plugin_id, "settings": settings}

    @staticmethod
    def update_plugin_settings(db, vendor_id, patch):
        from app.plugin_registry import PluginRegistry
        from app.utils.vendor_settings import save_plugin_settings as persist_plugin_settings

        vendor = VendorRepository(db).get_by_id(vendor_id)
        if not vendor or not vendor.plugin_id:
            return None, {"error": "vendor has no plugin"}

        schema = {s.key: s for s in PluginRegistry.get_settings(vendor.plugin_id)}
        errors = {}
        for key, value in patch.items():
            if key not in schema:
                errors[key] = "unknown_setting"
            elif not schema[key].validate(value):
                errors[key] = "invalid_value"

        if errors:
            return None, errors

        persist_plugin_settings(vendor, vendor.plugin_id, patch)
        return vendor, {}
