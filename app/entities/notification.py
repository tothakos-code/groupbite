import enum
from sqlalchemy import ForeignKey, select, exc
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SAEnum
from . import Base, session
from uuid import UUID
import logging
from app.services.encrypted_type import Encrypted

class NotificationType(enum.Enum):
    CLOSING = "closing" # sent when the order is closed
    REMINDER = "reminder" # sent at a fix time set in vendor settings if the user not participating in the order yet
    FAVOURITE = "favourite" # sent when a favourite item is on today's menu

    def __str__(self):
        return self.value

class Notification(Base):
    __tablename__ = "notification"

    vendor_id: Mapped[UUID] = mapped_column(ForeignKey("vendor.id"), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), primary_key=True)
    endpoint: Mapped[str] = mapped_column(primary_key=True)
    p256dh: Mapped[str] = mapped_column(Encrypted())
    auth: Mapped[str] = mapped_column(Encrypted())
    notification_types = mapped_column(
        ARRAY(SAEnum(NotificationType, name='notificationtype', create_type=False)),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="notifications")

    def find_all():
        stmt = select(Notification)
        return session.execute(stmt).scalars().all()

    def find_all_by_vendor(vendor_id):
        stmt = select(Notification).where(Notification.vendor_id == vendor_id)
        return session.execute(stmt).scalars().all()

    def find_by_vendor_id(vendor_id, notification_type):
        stmt = select(Notification).where(
            Notification.vendor_id == vendor_id,
            Notification.notification_types.contains([notification_type]),
        )
        return session.execute(stmt).scalars().all()

    def find_by_vendor_id_user_id(vendor_id, user_id, notification_type):
        stmt = select(Notification).where(
            Notification.vendor_id == vendor_id,
            Notification.user_id == user_id,
            Notification.notification_types.contains([notification_type]),
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
            new_types = [t for t in notification.notification_types if t not in noti.notification_types]
            if new_types:
                noti.notification_types = noti.notification_types + new_types
                try:
                    session.commit()
                except Exception as e:
                    logging.exception("Error updating notification types")
                    session.rollback()
                    return False, None
            return True, noti

        session.add(notification)
        try:
            session.commit()
            session.refresh(notification)
            return True, notification
        except exc.DataError as e:
            logging.exception("DataError during notification add")
            session.rollback()
            return False, None
        except Exception as e:
            logging.exception("Unhandled exception happened, rolling back")
            session.rollback()
            return False, None

    def remove_type_for_user(vendor_id, user_id, notification_type):
        """Remove a notification type from all device subscriptions for this vendor+user.
        Deletes rows that become empty."""
        rows = Notification.find_by_vendor_id_user_id(vendor_id, user_id, notification_type)
        for noti in rows:
            remaining = [t for t in noti.notification_types if t != notification_type]
            if remaining:
                noti.notification_types = remaining
            else:
                session.delete(noti)
        try:
            session.commit()
        except Exception as e:
            logging.exception("Error removing notification type for user")
            session.rollback()

    def remove_type_for_device(vendor_id, user_id, endpoint, notification_type):
        """Remove a notification type from a specific device subscription.
        Deletes the row if it becomes empty."""
        noti = Notification.find_by_pk(vendor_id, user_id, endpoint)
        if not noti or notification_type not in noti.notification_types:
            return
        remaining = [t for t in noti.notification_types if t != notification_type]
        if remaining:
            noti.notification_types = remaining
        else:
            session.delete(noti)
        try:
            session.commit()
        except Exception as e:
            logging.exception("Error removing notification type for device")
            session.rollback()

    def delete(self):
        session.delete(self)
        try:
            session.commit()
            return True
        except exc.DataError as e:
            logging.exception("DataError during notification delete")
            session.rollback()
            return False
        except exc.IntegrityError as e:
            logging.exception("IntegrityError during notification delete")
            session.rollback()
            return False
        except Exception as e:
            logging.exception("Unhandled exception happened, rolling back")
            session.rollback()
            return False

    @property
    def serialized(self):
        return {
            "vendor_id": str(self.vendor_id),
            "user_id": str(self.user_id),
            "notification_types": [str(t) for t in self.notification_types],
            "endpoint": self.endpoint
        }
