from uuid import UUID

from sqlalchemy import select

from app.entities.user_favourite import UserFavourite


class FavouriteRepository:
    def __init__(self, db):
        self.db = db

    def find_by_user_and_vendor(self, user_id: UUID, vendor_id: UUID):
        stmt = select(UserFavourite).where(
            UserFavourite.user_id == user_id,
            UserFavourite.vendor_id == vendor_id,
        )
        return self.db.execute(stmt).scalars().all()

    def find_by_id(self, favourite_id: UUID):
        stmt = select(UserFavourite).where(UserFavourite.id == favourite_id)
        return self.db.execute(stmt).scalars().first()

    def find_by_user(self, user_id: UUID):
        stmt = select(UserFavourite).where(UserFavourite.user_id == user_id)
        return self.db.execute(stmt).scalars().all()

    def find_by_vendor(self, vendor_id: UUID):
        stmt = select(UserFavourite).where(UserFavourite.vendor_id == vendor_id)
        return self.db.execute(stmt).scalars().all()

    def save(self, favourite: UserFavourite) -> UserFavourite:
        self.db.add(favourite)
        self.db.flush()
        return favourite

    def delete(self, favourite: UserFavourite) -> None:
        self.db.delete(favourite)
        self.db.flush()
