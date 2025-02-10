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
from marshmallow import Schema, fields
from .notification import NotificationType
from app.entities.setting import Setting

DEFAULT_VENDOR_SETTINGS = {
  "link": {
    "name": "Eredeti oldal elérhetősége",
    "type": "STR",
    "value": "",
    "section": "general"
  },
  "title": {
    "name": "Cím",
    "type": "STR",
    "value": "",
    "section": "general"
  },
  "comment_example": {
    "name": "Rendelés megjegyzés példa",
    "type": "STR",
    "value": "",
    "section": "general"
  },
  "transport_price": {
    "name": "Szállítási díj",
    "type": "INT",
    "value": "0",
    "section": "general"
  },
  "auto_email_order": {
    "name": "Automatikus email rendelés",
    "type": "BOOL",
    "value": False,
    "section": "auto-order"
  },
  "email_order_scheduler": {
    "name": "Rendelés automatikus email küldése (formátum: hh:mm)",
    "type": "STR",
    "value": "",
    "section": "auto-order"
  },
  "closed_scheduler_active": {
    "name": "",
    "type": "BOOL",
    "value": False,
    "section": "order"
  },
  "closure_scheduler_active": {
    "name": "",
    "type": "BOOL",
    "value": False,
    "section": "order"
  },
  "closed_scheduler": {
    "name": "Rendelés automatikus lezárása (formátum: hh:mm)",
    "type": "STR",
    "value": "",
    "section": "order"
  },
  "closure_scheduler": {
    "name": "Rendelés automatikus zárás figyelmeztetés (formátum: hh:mm)",
    "type": "STR",
    "value": "",
    "section": "order"
  },
  "auto_email_order_to": {
    "name": "Automatikus rendelés címzett",
    "type": "LIST",
    "value": [],
    "section": "auto-order"
  },
  "auto_email_order_cc": {
    "name": "Automatikus rendelés másolatot kap",
    "type": "LIST",
    "value": [],
    "section": "auto-order"
  },
  "order_text_template": {
    "name": "Rendelés szöveg sor minta",
    "type": "STR",
    "value": "${quantity}x ${item_name} ${size_name}\\n",
    "section": "order"
  },
  "auto_email_order_template": {
    "name": "Automatikus rendelés üzenet sablon",
    "type": "STRBOX",
    "value": "",
    "section": "auto-order"
  }
}



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
        if not isinstance(self.settings, dict):
            self.settings = {}
        self.settings = {**DEFAULT_VENDOR_SETTINGS, **self.settings}

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

    def update_settings(self, settings):
        closure_scheduler_active_changed = self.settings["closure_scheduler_active"]["value"] != settings["closure_scheduler_active"]["value"]
        closure_scheduler_changed = self.settings["closure_scheduler"]["value"] != settings["closure_scheduler"]["value"]
        if closure_scheduler_active_changed or closure_scheduler_changed:
            from app.scheduler import schedule_task, cancel_task
            cancel_task(str(self.id) + "-closure")

            if settings["closure_scheduler_active"]["value"]:
                hh, mm = settings["closure_scheduler"]["value"].split(":")
                schedule_task(str(self.id) + "-closure", int(hh), int(mm), self.closure_wrapper)

        closed_scheduler_active_changed = self.settings["closed_scheduler_active"]["value"] != settings["closed_scheduler_active"]["value"]
        closed_scheduler_changed = self.settings["closed_scheduler"]["value"] != settings["closed_scheduler"]["value"]
        if closed_scheduler_active_changed or closed_scheduler_changed:
            from app.scheduler import schedule_task, cancel_task
            cancel_task(str(self.id) + "-closed")

            if settings["closed_scheduler_active"]["value"]:
                hh, mm = settings["closed_scheduler"]["value"].split(":")
                schedule_task(str(self.id) + "-closed", int(hh), int(mm), self.closed_wrapper)

        auto_email_order_changed = self.settings["auto_email_order"]["value"] != settings["auto_email_order"]["value"]
        if settings["auto_email_order"]["value"] and Setting.get_value_by_key(smtp_address) != "":
            email_scheduler_changed = self.settings["email_order_scheduler"]["value"] != settings["email_order_scheduler"]["value"]
            if auto_email_order_changed or email_scheduler_changed:
                from app.scheduler import schedule_task, cancel_task
                cancel_task(str(self.id) + "-email-order")

                if settings["auto_email_order"]["value"]:
                    hh, mm = settings["email_order_scheduler"]["value"].split(":")
                    schedule_task(str(self.id) + "-email-order", int(hh), int(mm), self.email_ordering_wrapper)
        else:
            logging.warning("No SMPT server set")
            settings["auto_email_order"]["value"] = self.settings["auto_email_order"]["value"]
            settings["email_order_scheduler"]["value"] = self.settings["email_order_scheduler"]["value"]

        self.settings = settings;
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


    def update_setting(self, key, value):
        if key not in self.settings:
            return False
        settings = self.settings
        settings[key]["value"] = value
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
            logging.exception("Unhadled exception happened, rolling back")
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


            if vendor_db.settings["closure_scheduler_active"]["value"]:
                from app.scheduler import schedule_task, cancel_task
                hh, mm = vendor_db.settings["closure_scheduler"]["value"].split(":")
                schedule_task(str(vendor_db.id) + "-closure", int(hh), int(mm), vendor_db.closure_wrapper)

            if vendor_db.settings["closed_scheduler_active"]["value"]:
                from app.scheduler import schedule_task, cancel_task
                hh, mm = vendor_db.settings["closed_scheduler"]["value"].split(":")
                schedule_task(str(vendor_db.id) + "-closed", int(hh), int(mm), vendor_db.closed_wrapper)

            if vendor_db.settings["auto_email_order"]["value"]:
                from app.scheduler import schedule_task, cancel_task
                hh, mm = vendor_db.settings["email_order_scheduler"]["value"].split(":")
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
        if order:
            from app.socketio_singleton import SocketioSingleton
            order.change_state(OrderState.CLOSED, None)
            socketio = SocketioSingleton.get_instance()
            socketio.emit("be_order_update", {
                "order": order.serialized
            })
        else:
            logging.info("State already changed")

    def email_ordering_wrapper(self):
        logging.info("Scheduled email ordering running")
        from app.entities.order import Order, OrderState

        order = Order.find_order_by_date_for_a_vendor(str(self.id), date.today().strftime("%Y-%m-%d"))
        if order:
            if self.settings["auto_email_order"]["value"] == True:
                from app.services.mail_sender_service import send_mail
                from app.entities.user_basket import UserBasket
                baskets = UserBasket.find_items_by_order(order.id)
                if len(baskets) == 0:
                    logging.info("The order is empty, email not sent")
                    return
                basket_template = ""
                basket_categories = {}
                for basket in baskets:
                    pattern = self.settings["order_text_template"]["value"]
                    line = pattern \
                        .replace("${quantity}", str(basket.count)) \
                        .replace("${item_name}", basket.item.name) \
                        .replace("${size_name}", basket.size.name) \
                        .replace("\\n", "<br>")
                    basket_template += line

                    if basket.item.category not in basket_categories:
                        basket_categories[basket.item.category] = ""
                    basket_categories[basket.item.category] += line

                email_template = self.settings["auto_email_order_template"]["value"]
                email_template = email_template.replace("${basket}", basket_template)
                for category, value in basket_categories.items():
                    email_template = email_template.replace("${basket." + category + "}", basket_categories[category])


                logging.info("Scheduled automatic order email sent!")
                send_mail(
                    self.settings["auto_email_order_to"]["value"],
                    self.settings["auto_email_order_cc"]["value"],
                    self.settings["title"]["value"] + " rendelés",
                    email_template)

        else:
            logging.info("Order not found")


    @property
    def serialized(self):
        # from app.vendor_factory import VendorFactory
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
