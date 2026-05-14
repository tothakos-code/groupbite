from sqlalchemy import select

from app.entities.stock_history import StockHistory, StockChangeReason


class StockHistoryRepository:
    def __init__(self, db):
        self.db = db

    def save(self, entry: StockHistory) -> StockHistory:
        self.db.add(entry)
        self.db.flush()
        return entry

    def find_by_size(self, size_id, from_date=None, to_date=None) -> list[StockHistory]:
        stmt = select(StockHistory).where(StockHistory.size_id == size_id)
        if from_date is not None:
            stmt = stmt.where(StockHistory.timestamp >= from_date)
        if to_date is not None:
            stmt = stmt.where(StockHistory.timestamp <= to_date)
        stmt = stmt.order_by(StockHistory.timestamp.asc())
        return self.db.execute(stmt).scalars().all()

    def find_last_topup_for_vendor(self, vendor_id) -> StockHistory | None:
        from app.entities.size import Size
        from app.entities.menu_item import MenuItem
        from app.entities.menu import Menu

        stmt = (
            select(StockHistory)
            .join(Size, StockHistory.size_id == Size.id)
            .join(MenuItem, Size.menu_item_id == MenuItem.id)
            .join(Menu, MenuItem.menu_id == Menu.id)
            .where(
                Menu.vendor_id == vendor_id,
                StockHistory.reason == StockChangeReason.TOPUP,
            )
            .order_by(StockHistory.timestamp.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalars().first()
