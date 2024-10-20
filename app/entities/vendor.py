from enum import Enum as pyenum
from sqlalchemy.dialects.postgresql import JSONB
from . import Base, session
from datetime import date
from sqlalchemy import Boolean, select, exc
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from uuid import UUID, uuid4
from typing import List
import logging
from marshmallow import Schema, fields
from .notification import NotificationType

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
        if self.settings["closure_scheduler"]["value"] != settings["closure_scheduler"]["value"]:
            from app.scheduler import schedule_task, cancel_task
            cancel_task(str(self.id) + "-closure")

            if settings["closure_scheduler"]["value"] != "manual":
                hh, mm = settings["closure_scheduler"]["value"].split(":")
                schedule_task(str(self.id) + "-closure", int(hh), int(mm), self.closure_wrapper)

        if self.settings["closed_scheduler"]["value"] != settings["closed_scheduler"]["value"]:
            from app.scheduler import schedule_task, cancel_task
            cancel_task(str(self.id) + "-closed")

            if settings["closed_scheduler"]["value"] != "manual":
                hh, mm = settings["closed_scheduler"]["value"].split(":")
                schedule_task(str(self.id) + "-closed", int(hh), int(mm), self.closed_wrapper)

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

    def add_vendor(vendor_obj):
        stmt = select(Vendor).where(Vendor.name == vendor_obj.name)
        vendor_db = session.execute(stmt).scalars().first()

        if not vendor_db:
            # insert
            vendor_id = uuid4()
            session.add(Vendor(id=vendor_id, name=vendor_obj.name, type=vendor_obj.type, settings=vendor_obj.settings))
            vendor_obj.id = str(vendor_id)
            logging.info("Vendor registered in database: {0}".format(vendor_obj.name))
        else:
            vendor_obj.id = str(vendor_db.id)
            logging.info(vendor_db.settings)

            if vendor_db.settings["closure_scheduler"]["value"] != "manual":
                from app.scheduler import schedule_task, cancel_task
                hh, mm = vendor_db.settings["closure_scheduler"]["value"].split(":")
                schedule_task(str(vendor_db.id) + "-closure", int(hh), int(mm), vendor_db.closure_wrapper)

            if vendor_db.settings["closed_scheduler"]["value"] != "manual":
                from app.scheduler import schedule_task, cancel_task
                hh, mm = vendor_db.settings["closed_scheduler"]["value"].split(":")
                schedule_task(str(vendor_db.id) + "-closed", int(hh), int(mm), vendor_db.closed_wrapper)

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
            # order.change_state(OrderState.CLOSED, None)
            if self.settings["auto_email_order"]["value"] == True:
                from app.services.mail_sender_service import send_mail
                from app.entities.user_basket import UserBasket
                baskets = UserBasket.find_items_by_order(order.id)
                email_body = ""
                for basket in baskets:
                    pattern = self.settings["order_text_template"]["value"]
                    email_body += pattern \
                        .replace("${quantity}", str(basket.count)) \
                        .replace("${item_name}", basket.item.name) \
                        .replace("${size_name}", basket.size.name) \
                        .replace("\\n", "<br>")

                email_template = self.settings["auto_email_order_template"]["value"]
                email_template = email_template.replace("${basket}", email_body)
                logging.info("Scheduled automatic order email sent!")
                send_mail(self.settings["auto_email_order_to"]["value"], "Makkos rendelés", email_template)

            socketio = SocketioSingleton.get_instance()
            socketio.emit("be_order_update", {
                "order": order.serialized
            })
        else:
            logging.info("State already changed")


    @property
    def serialized(self):
        from app.vendor_factory import VendorFactory
        return {
            "id": str(self.id),
            "name": self.name,
            "active": self.active,
            "type": str(self.type),
            "settings": self.settings,
        }
