from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from . import Base

access_group_member = Table(
    "access_group_member",
    Base.metadata,
    Column("access_group_id", ForeignKey("access_group.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
)

access_group_vendor = Table(
    "access_group_vendor",
    Base.metadata,
    Column("access_group_id", ForeignKey("access_group.id", ondelete="CASCADE"), primary_key=True),
    Column("vendor_id", ForeignKey("vendor.id", ondelete="CASCADE"), primary_key=True),
)


class AccessGroup(Base):
    """A named group of users that grants its members manager-level access to a set of vendors.

    Pilot for a future self-service groups feature: creation/membership/vendor
    assignment is admin-only for now, but the shape (group <-> users, group <-> vendors)
    is the same one users will eventually manage themselves.
    """

    __tablename__ = "access_group"

    id: Mapped[UUID] = mapped_column(primary_key=True, unique=True, nullable=False, default=uuid4)
    name: Mapped[str] = mapped_column(Text, unique=True)
    created_by: Mapped[Optional[UUID]] = mapped_column(ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    members: Mapped[List["User"]] = relationship(secondary=access_group_member)
    vendors: Mapped[List["Vendor"]] = relationship(secondary=access_group_vendor)

    def __repr__(self):
        return f"AccessGroup<{self.id},name={self.name}>"

    @property
    def serialized(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "created_by": str(self.created_by) if self.created_by else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "members": [{"id": str(u.id), "username": u.username} for u in self.members],
            "vendors": [{"id": str(v.id), "name": v.name} for v in self.vendors],
        }
