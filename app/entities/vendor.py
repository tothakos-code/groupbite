from enum import Enum as pyenum
from sqlalchemy.dialects.postgresql import JSONB
from . import Base, session
from datetime import date
from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from uuid import UUID, uuid4
from typing import List
import logging


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
        return session.query(Vendor).order_by(Vendor.name).all()

    def find_all_by_type(type):
        return session.query(Vendor).where(Vendor.type == type).all()

    def find_all_active():
        return session.query(Vendor).where(Vendor.active == True).all()

    def find_by_id(id):
        return session.query(Vendor).where(Vendor.id == id).first()

    def activate(self):
        self.active = True;
        session.commit()

    def deactivate(self):
        self.active = False;
        session.commit()

    def update_settings(self, settings):
        if self.settings["closure_scheduler"]["value"] != settings["closure_scheduler"]["value"]:
            from app.scheduler import schedule_task, cancel_task
            cancel_task(self.id)


            if settings["closure_scheduler"]["value"] != "manual":

                from app.socketio_singleton import SocketioSingleton

                def closure_wrapper():
                    logging.info("Scheduled order state stepping running")
                    from app.entities.order import Order, OrderState

                    order = Order.find_open_order_by_date_for_a_vendor(self.id, date.today().strftime("%Y-%m-%d"))
                    if order:
                        order.change_state(OrderState.ORDER, None)

                        socketio = SocketioSingleton.get_instance()
                        socketio.emit("be_order_update", {
                            "order": order.serialized
                        })
                    else:
                        logging.info("State already changed")


                hh, mm = settings["closure_scheduler"]["value"].split(":")
                schedule_task(str(self.id), int(hh), int(mm), closure_wrapper)

        self.settings = settings;
        session.commit()

    def add_vendor(vendor_obj):
        vendor_db = session.query(Vendor).filter_by(name = vendor_obj.name).first()

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
                from app.socketio_singleton import SocketioSingleton

                def closure_wrapper():
                    logging.info("Scheduled order state stepping running")
                    from app.entities.order import Order, OrderState

                    order = Order.find_open_order_by_date_for_a_vendor(str(vendor_db.id), date.today().strftime("%Y-%m-%d"))
                    if order:
                        order.change_state(OrderState.ORDER, None)

                        socketio = SocketioSingleton.get_instance()
                        socketio.emit("be_order_update", {
                            "order": order.serialized
                        })
                    else:
                        logging.info("State already changed")


                hh, mm = settings["closure_scheduler"]["value"].split(":")
                schedule_task(str(vendor_db.id), int(hh), int(mm), closure_wrapper)

        session.commit()


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
