import logging

from flask import session

from app.repositories.setting_repository import SettingRepository
from app.repositories.user_repository import UserRepository
from app.repositories.vendor_repository import VendorRepository
from app.services.encrypted_type import encrypt_value
from app.services.vendor_service import VendorService


class SettingService:
    def __init__(self, vendor_service: VendorService) -> None:
        self.vendor_service = vendor_service

    def update_setting(self, db, key, value):
        setting = SettingRepository(db).get_setting_by_key(key)
        if setting:
            if setting.key == "smtp_password":
                if value != setting.value:
                    setting.value = encrypt_value(value)
            elif setting.key == "smtp_address" and value == "":
                vendors = VendorRepository(db).find_all()
                for vendor in vendors:
                    self.vendor_service.update_setting(
                        vendor, "auto_email_order", False
                    )
                setting.value = value
            else:
                setting.value = value
            db.commit()
            return True
        return False

    @staticmethod
    def get_setting(db, key):
        setting = SettingRepository(db).get_setting_by_key(key)
        if setting:
            if setting.category != "application":
                if "user_id" not in session:
                    logging.warning("User not authenticated")
                    raise PermissionError("User not authenticated")

                if not UserRepository(db).is_admin(session["user_id"]):
                    logging.warning("User unauthorized")
                    raise PermissionError("User unauthorized")

            return setting
        raise ValueError("Setting not found")
