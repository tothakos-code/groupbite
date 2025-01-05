import enum
from sqlalchemy import ForeignKey, select, exc
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from . import Base, session
from uuid import UUID
import logging
from app.services.encrypted_type import Encrypted

class NotificationType(enum.Enum):
    CLOSING = "closing" # sent when the order is closed
    REMINDER = "reminder" # sent at a fix time set in vendor settings if the user not participating in the order yet

    def __str__(self):
        return self.value

class Notification(Base):
    __tablename__ = "notification"

    vendor_id: Mapped[UUID] = mapped_column(ForeignKey("vendor.id"), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), primary_key=True)
    notification_type: Mapped[NotificationType]
    endpoint: Mapped[str] = mapped_column(primary_key=True)
    p256dh: Mapped[str] = mapped_column(Encrypted())
    auth: Mapped[str] = mapped_column(Encrypted())

    user: Mapped["User"] = relationship(back_populates="notifications")


    def find_all():
        stmt = select(Notification)
        return session.execute(stmt).scalars().all()


    def find_by_vendor_id(vendor_id, notification_type):
        stmt = select(Notification).where(
            Notification.vendor_id == vendor_id,
            Notification.notification_type == notification_type
        )
        return session.execute(stmt).scalars().all()


    def find_by_vendor_id_user_id(vendor_id, user_id, notification_type):
        stmt = select(Notification).where(
            Notification.vendor_id == vendor_id,
            Notification.user_id == user_id,
            Notification.notification_type == notification_type
        )
        return session.execute(stmt).scalars().all()

    def find_by_pk(vendor_id, user_id, endpoint):
        stmt = select(Notification).where(
            Notification.vendor_id == vendor_id,
            Notification.user_id == user_id,
            Notification.endpoint == endpoint
        )
        return session.execute(stmt).scalars().first()

    def add(notification):
        noti = Notification.find_by_pk(notification.vendor_id, notification.user_id, notification.endpoint)
        if noti:
            logging.warning(f"Notification already exist for vendor:{notification.vendor_id} user:{notification.user_id}, endpoint:{notification.endpoint}")
            return True, noti

        session.add(notification)
        try:
            session.commit()
            session.refresh(notification)
            return True, notification
        except exc.DataError as e:
            logging.exception("DataError during menuitem add")
            session.rollback()
            return False, None
        except Exception as e:
            logging.exception("Unhadled exception happened, rolling back")
            session.rollback()
            return False, None

    def delete(self):
        session.delete(self)
        try:
            session.commit()
            return True
        except exc.DataError as e:
            logging.exception("DataError during menuitem update")
            session.rollback()
            return False
        except exc.IntegrityError as e:
            logging.exception("IntegrityError during Menu delete")
            session.rollback()
            return False
        except Exception as e:
            logging.exception("Unhadled exception happened, rolling back")
            session.rollback()
            return False

    @property
    def serialized(self):
        return {
            "vendor_id": str(self.vendor_id),
            "user_id": str(self.user_id),
            "notification_type": str(self.notification_type)
        }
