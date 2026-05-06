from sqlalchemy import select

from app.entities.option_choice import OptionChoice


class OptionChoiceRepository:
    def __init__(self, db):
        self.db = db

    def find_by_group(self, option_group_id: int) -> list:
        stmt = (
            select(OptionChoice)
            .where(OptionChoice.option_group_id == option_group_id, OptionChoice.active == True)
            .order_by(OptionChoice.index)
        )
        return self.db.execute(stmt).scalars().all()

    def find_by_id_include_inactive(self, choice_id: int):
        stmt = select(OptionChoice).where(OptionChoice.id == choice_id)
        return self.db.execute(stmt).scalars().first()

    def save(self, choice: OptionChoice) -> OptionChoice:
        self.db.add(choice)
        self.db.flush()
        return choice

    def soft_delete(self, choice_id: int):
        choice = self.find_by_id_include_inactive(choice_id)
        if choice:
            choice.active = False
            self.db.flush()
