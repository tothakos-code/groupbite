import logging

from sqlalchemy import text

from app.db.session import get_session


def run_daily_cleanup():
    with get_session() as db:
        from app.repositories.order_repository import OrderRepository
        deleted_orders = OrderRepository(db).delete_old_empty_collect_orders(days=7)
        result = db.execute(text("DELETE FROM sessions WHERE expiry < NOW()"))
        deleted_sessions = result.rowcount
    logging.info(
        "Daily cleanup: removed %d empty collect orders, %d expired sessions",
        deleted_orders,
        deleted_sessions,
    )
