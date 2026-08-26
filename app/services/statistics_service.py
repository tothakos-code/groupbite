from datetime import date, timedelta

from sqlalchemy import case, distinct, func, select

from app.entities.category import Category
from app.entities.menu import Menu
from app.entities.menu_item import MenuItem
from app.entities.order import Order, OrderState
from app.entities.order_item import OrderItem
from app.entities.size import Size
from app.entities.stock_history import StockChangeReason, StockHistory
from app.entities.user import User
from app.repositories.stock_history_repository import StockHistoryRepository


class StatisticsService:

    @staticmethod
    def get_stock_summary(db, vendor_id) -> dict:
        base_stmt = (
            select(func.count(Size.id))
            .join(MenuItem, Size.menu_item_id == MenuItem.id)
            .join(Menu, MenuItem.menu_id == Menu.id)
            .where(Menu.vendor_id == vendor_id, Size.unlimited.is_(False))
        )
        total_limited = db.execute(base_stmt).scalar() or 0
        out_of_stock = db.execute(base_stmt.where(Size.quantity == 0)).scalar() or 0
        low_stock = db.execute(
            base_stmt.where(Size.quantity > 0, Size.quantity < 10)
        ).scalar() or 0
        return {
            "out_of_stock": out_of_stock,
            "low_stock": low_stock,
            "total_limited": total_limited,
        }

    @staticmethod
    def get_sales_trend(db, vendor_id, from_date=None, to_date=None) -> dict:
        if to_date is None:
            to_date = date.today()
        if from_date is None:
            from_date = to_date - timedelta(days=30)

        # Unbounded/very wide ranges would otherwise produce one row per calendar day.
        use_month = from_date is None or (to_date - from_date).days > 90

        if use_month:
            period_expr = func.to_char(Order.open_from, "YYYY-MM").label("period")
        else:
            period_expr = Order.open_from.label("period")

        stmt = (
            select(
                period_expr,
                func.count(Order.id).label("order_count"),
                func.coalesce(func.sum(Order.total_price), 0).label("revenue"),
            )
            .where(
                Order.vendor_id == vendor_id,
                Order.state_id == OrderState.CLOSED,
                Order.open_from <= to_date,
            )
            .group_by("period")
            .order_by("period")
        )
        if from_date is not None:
            stmt = stmt.where(Order.open_from >= from_date)

        rows = db.execute(stmt).all()

        if use_month:
            result = [
                {"date": row.period, "revenue": row.revenue, "order_count": row.order_count}
                for row in rows
            ]
        else:
            rows_by_date = {row.period: row for row in rows}
            result = []
            current = from_date
            while current <= to_date:
                row = rows_by_date.get(current)
                result.append({
                    "date": current.strftime("%Y-%m-%d"),
                    "revenue": row.revenue if row else 0,
                    "order_count": row.order_count if row else 0,
                })
                current += timedelta(days=1)

        return {
            "from_date": from_date.strftime("%Y-%m-%d") if from_date else None,
            "to_date": to_date.strftime("%Y-%m-%d"),
            "granularity": "month" if use_month else "day",
            "sales": result,
        }

    @staticmethod
    def get_popular_items(db, vendor_id, from_date=None, to_date=None) -> list[dict]:
        stmt = (
            select(
                OrderItem.menu_item_id.label("item_id"),
                OrderItem.item_name.label("name"),
                func.sum(OrderItem.count).label("count"),
                func.sum(OrderItem.total_price).label("revenue"),
            )
            .join(Order, OrderItem.order_id == Order.id)
            .where(
                Order.vendor_id == vendor_id,
                Order.state_id == OrderState.CLOSED,
            )
            .group_by(OrderItem.menu_item_id, OrderItem.item_name)
            .order_by(func.sum(OrderItem.count).desc())
            .limit(10)
        )
        if from_date is not None:
            stmt = stmt.where(Order.open_from >= from_date)
        if to_date is not None:
            stmt = stmt.where(Order.open_from <= to_date)

        return [
            {
                "item_id": row.item_id,
                "name": row.name,
                "count": row.count,
                "revenue": row.revenue,
            }
            for row in db.execute(stmt).all()
        ]

    @staticmethod
    def get_per_user_spend(db, vendor_id, from_date=None, to_date=None) -> list[dict]:
        stmt = (
            select(
                OrderItem.user_id,
                User.username,
                func.sum(OrderItem.total_price).label("total_spend"),
                func.count(distinct(OrderItem.order_id)).label("order_count"),
            )
            .join(Order, OrderItem.order_id == Order.id)
            .join(User, OrderItem.user_id == User.id)
            .where(
                Order.vendor_id == vendor_id,
                Order.state_id == OrderState.CLOSED,
            )
            .group_by(OrderItem.user_id, User.username)
            .order_by(func.sum(OrderItem.total_price).desc())
        )
        if from_date is not None:
            stmt = stmt.where(Order.open_from >= from_date)
        if to_date is not None:
            stmt = stmt.where(Order.open_from <= to_date)

        return [
            {
                "user_id": str(row.user_id),
                "username": row.username,
                "total_spend": row.total_spend,
                "order_count": row.order_count,
            }
            for row in db.execute(stmt).all()
        ]

    @staticmethod
    def get_vendor_trend(db, vendor_id, from_date=None, to_date=None) -> list[dict]:
        if from_date is None:
            from_date = date.today() - timedelta(days=90)
        if to_date is None:
            to_date = date.today()

        use_month = (to_date - from_date).days > 90
        if use_month:
            period_expr = func.to_char(Order.open_from, "YYYY-MM").label("period_label")
        else:
            period_expr = func.to_char(Order.open_from, 'IYYY-"W"IW').label("period_label")

        stmt = (
            select(
                period_expr,
                func.count(Order.id).label("order_count"),
                func.coalesce(func.sum(Order.total_price), 0).label("revenue"),
            )
            .where(
                Order.vendor_id == vendor_id,
                Order.state_id == OrderState.CLOSED,
                Order.open_from >= from_date,
                Order.open_from <= to_date,
            )
            .group_by("period_label")
            .order_by("period_label")
        )

        return [
            {
                "period_label": row.period_label,
                "order_count": row.order_count,
                "revenue": row.revenue,
            }
            for row in db.execute(stmt).all()
        ]

    @staticmethod
    def get_kpi_summary(db, vendor_id) -> dict:
        base_where = [
            Order.vendor_id == vendor_id,
            Order.state_id == OrderState.CLOSED,
        ]

        total_revenue = db.execute(
            select(func.coalesce(func.sum(Order.total_price), 0)).where(*base_where)
        ).scalar()

        avg_order_value = db.execute(
            select(func.coalesce(func.avg(Order.total_price), 0)).where(*base_where)
        ).scalar()

        thirty_days_ago = date.today() - timedelta(days=30)
        orders_last_30d = db.execute(
            select(func.count(Order.id)).where(
                *base_where, Order.open_from >= thirty_days_ago
            )
        ).scalar() or 0
        orders_per_day = round(orders_last_30d / 30, 2)

        popular_row = db.execute(
            select(OrderItem.item_name)
            .join(Order, OrderItem.order_id == Order.id)
            .where(*base_where)
            .group_by(OrderItem.item_name)
            .order_by(func.sum(OrderItem.count).desc())
            .limit(1)
        ).scalar()
        most_popular_item = popular_row or "N/A"

        return {
            "total_revenue": int(total_revenue),
            "avg_order_value": round(float(avg_order_value), 2),
            "orders_per_day": orders_per_day,
            "most_popular_item": most_popular_item,
        }

    @staticmethod
    def get_stock_alerts(db, vendor_id) -> list[dict]:
        stmt = (
            select(
                MenuItem.name.label("item_name"),
                Size.name.label("size_name"),
                Size.id.label("size_id"),
                Size.quantity,
                case(
                    (Size.quantity == 0, "out_of_stock"),
                    (Size.quantity < 5, "critical"),
                    else_="low",
                ).label("alert_level"),
            )
            .join(MenuItem, Size.menu_item_id == MenuItem.id)
            .join(Menu, MenuItem.menu_id == Menu.id)
            .where(
                Menu.vendor_id == vendor_id,
                Size.unlimited.is_(False),
                Size.quantity < 10,
            )
            .order_by(Size.quantity.asc())
        )

        return [
            {
                "item_name": row.item_name,
                "size_name": row.size_name,
                "size_id": row.size_id,
                "quantity": row.quantity,
                "alert_level": row.alert_level,
            }
            for row in db.execute(stmt).all()
        ]

    @staticmethod
    def get_depletion_rates(db, vendor_id, from_date=None, to_date=None) -> list[dict]:
        if to_date is None:
            to_date = date.today()
        if from_date is None:
            from_date = to_date - timedelta(days=30)

        days_span = max((to_date - from_date).days, 1)
        depleted_expr = func.sum(-StockHistory.quantity_change)

        stmt = (
            select(
                MenuItem.id.label("item_id"),
                MenuItem.name.label("item_name"),
                Size.id.label("size_id"),
                Size.name.label("size_name"),
                depleted_expr.label("total_depleted"),
            )
            .join(Size, StockHistory.size_id == Size.id)
            .join(MenuItem, Size.menu_item_id == MenuItem.id)
            .join(Menu, MenuItem.menu_id == Menu.id)
            .where(
                Menu.vendor_id == vendor_id,
                StockHistory.reason == StockChangeReason.ORDER,
                StockHistory.timestamp >= from_date,
                StockHistory.timestamp < to_date + timedelta(days=1),
            )
            .group_by(MenuItem.id, MenuItem.name, Size.id, Size.name)
            .having(depleted_expr > 0)
            .order_by(depleted_expr.desc())
        )

        return [
            {
                "item_id": row.item_id,
                "item_name": row.item_name,
                "size_id": row.size_id,
                "size_name": row.size_name,
                "total_depleted": int(row.total_depleted),
                "per_day": round(row.total_depleted / days_span, 2),
            }
            for row in db.execute(stmt).all()
        ]

    @staticmethod
    def resolve_date_preset(db, vendor_id, preset: str) -> tuple:
        today = date.today()

        if preset == "last_30_days":
            return today - timedelta(days=30), today

        if preset == "current_month":
            return today.replace(day=1), today

        if preset == "last_month":
            first_of_this = today.replace(day=1)
            last_of_prev = first_of_this - timedelta(days=1)
            first_of_prev = last_of_prev.replace(day=1)
            return first_of_prev, last_of_prev

        if preset == "since_last_topup":
            entry = StockHistoryRepository(db).find_last_topup_for_vendor(vendor_id)
            if entry:
                return entry.timestamp.date(), today
            return today - timedelta(days=30), today

        if preset == "all_time":
            return None, None

        return today - timedelta(days=30), today
