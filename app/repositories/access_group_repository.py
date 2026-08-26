from sqlalchemy import select

from app.entities.access_group import AccessGroup, access_group_member, access_group_vendor


class AccessGroupRepository:
    def __init__(self, db):
        self.db = db

    def save(self, group: AccessGroup) -> AccessGroup:
        self.db.add(group)
        self.db.flush()
        return group

    def get_by_id(self, group_id):
        stmt = select(AccessGroup).where(AccessGroup.id == group_id)
        return self.db.execute(stmt).scalars().first()

    def get_by_name(self, name):
        stmt = select(AccessGroup).where(AccessGroup.name == name)
        return self.db.execute(stmt).scalars().first()

    def find_all(self):
        stmt = select(AccessGroup).order_by(AccessGroup.name)
        return self.db.execute(stmt).scalars().all()

    def delete(self, group: AccessGroup):
        self.db.delete(group)
        self.db.flush()

    def add_member(self, group_id, user_id):
        exists = self.db.execute(
            select(access_group_member.c.user_id).where(
                access_group_member.c.access_group_id == group_id,
                access_group_member.c.user_id == user_id,
            )
        ).first()
        if exists:
            return
        self.db.execute(
            access_group_member.insert().values(access_group_id=group_id, user_id=user_id)
        )
        self.db.flush()

    def remove_member(self, group_id, user_id):
        self.db.execute(
            access_group_member.delete().where(
                access_group_member.c.access_group_id == group_id,
                access_group_member.c.user_id == user_id,
            )
        )
        self.db.flush()

    def add_vendor(self, group_id, vendor_id):
        exists = self.db.execute(
            select(access_group_vendor.c.vendor_id).where(
                access_group_vendor.c.access_group_id == group_id,
                access_group_vendor.c.vendor_id == vendor_id,
            )
        ).first()
        if exists:
            return
        self.db.execute(
            access_group_vendor.insert().values(access_group_id=group_id, vendor_id=vendor_id)
        )
        self.db.flush()

    def remove_vendor(self, group_id, vendor_id):
        self.db.execute(
            access_group_vendor.delete().where(
                access_group_vendor.c.access_group_id == group_id,
                access_group_vendor.c.vendor_id == vendor_id,
            )
        )
        self.db.flush()

    def is_manager_of(self, user_id, vendor_id) -> bool:
        stmt = (
            select(access_group_member.c.user_id)
            .join(
                access_group_vendor,
                access_group_vendor.c.access_group_id == access_group_member.c.access_group_id,
            )
            .where(
                access_group_member.c.user_id == user_id,
                access_group_vendor.c.vendor_id == vendor_id,
            )
            .limit(1)
        )
        return self.db.execute(stmt).first() is not None

    def list_managed_vendor_ids(self, user_id) -> list:
        stmt = (
            select(access_group_vendor.c.vendor_id)
            .join(
                access_group_member,
                access_group_member.c.access_group_id == access_group_vendor.c.access_group_id,
            )
            .where(access_group_member.c.user_id == user_id)
            .distinct()
        )
        return [row[0] for row in self.db.execute(stmt).all()]
