from app.entities.access_group import AccessGroup
from app.repositories.access_group_repository import AccessGroupRepository


class AccessGroupService:
    @staticmethod
    def get_all(db) -> list:
        return AccessGroupRepository(db).find_all()

    @staticmethod
    def create(db, name: str, created_by=None) -> AccessGroup:
        repo = AccessGroupRepository(db)
        if repo.get_by_name(name):
            raise ValueError("name_taken")
        group = AccessGroup(name=name, created_by=created_by)
        return repo.save(group)

    @staticmethod
    def rename(db, group_id, name: str) -> AccessGroup:
        repo = AccessGroupRepository(db)
        group = repo.get_by_id(group_id)
        if not group:
            raise ValueError(f"AccessGroup {group_id} not found")
        if name != group.name and repo.get_by_name(name):
            raise ValueError("name_taken")
        group.name = name
        repo.save(group)
        return group

    @staticmethod
    def delete(db, group_id):
        repo = AccessGroupRepository(db)
        group = repo.get_by_id(group_id)
        if not group:
            raise ValueError(f"AccessGroup {group_id} not found")
        repo.delete(group)

    @staticmethod
    def add_member(db, group_id, user_id):
        repo = AccessGroupRepository(db)
        if not repo.get_by_id(group_id):
            raise ValueError(f"AccessGroup {group_id} not found")
        repo.add_member(group_id, user_id)

    @staticmethod
    def remove_member(db, group_id, user_id):
        AccessGroupRepository(db).remove_member(group_id, user_id)

    @staticmethod
    def add_vendor(db, group_id, vendor_id):
        repo = AccessGroupRepository(db)
        if not repo.get_by_id(group_id):
            raise ValueError(f"AccessGroup {group_id} not found")
        repo.add_vendor(group_id, vendor_id)

    @staticmethod
    def remove_vendor(db, group_id, vendor_id):
        AccessGroupRepository(db).remove_vendor(group_id, vendor_id)

    @staticmethod
    def is_manager_of(db, user_id, vendor_id) -> bool:
        return AccessGroupRepository(db).is_manager_of(user_id, vendor_id)

    @staticmethod
    def list_managed_vendor_ids(db, user_id) -> list:
        return AccessGroupRepository(db).list_managed_vendor_ids(user_id)
