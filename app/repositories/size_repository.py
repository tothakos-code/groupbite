from app.entities.size import Size


class SizeRepository:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, size_id):
        return self.db.get(Size, size_id)

    def increment_quantity(self, size):
        size.quantity += 1
        self.db.flush()

    def decrement_quantity(self, size):
        size.quantity -= 1
        self.db.flush()