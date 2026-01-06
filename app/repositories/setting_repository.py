from sqlalchemy import select

from app.entities.setting import Setting


class SettingRepository:
    def __init__(self, db) -> None:
        self.db = db

    def get_all_settings(self):
        stmt = select(Setting).order_by(Setting.id)
        return self.db.execute(stmt).scalars().all()

    def get_all_settings_as_kv(self):
        stmt = select(Setting).order_by(Setting.id)
        settings = self.db.execute(stmt).scalars().all()
        return {setting.key: setting.value for setting in settings}

    def get_setting_by_key(self, key):
        stmt = select(Setting).where(Setting.key == key)
        return self.db.execute(stmt).scalars().first()

    def get_value_by_key(self, key):
        stmt = select(Setting).where(Setting.key == key)
        return self.db.execute(stmt).scalars().first().value
