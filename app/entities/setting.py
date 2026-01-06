from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class Setting(Base):
    __tablename__ = "setting"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(nullable=False)
    value: Mapped[str] = mapped_column(nullable=True)
    category: Mapped[str] = mapped_column(nullable=True)

    def __repr__(self):
        return f"Setting<id={self.id},key={self.key},value={self.value}>"

    @property
    def serialized(self):
        return {"id": self.id, "key": self.key, "value": self.value}
