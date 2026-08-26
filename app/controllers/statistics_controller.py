from datetime import date
from uuid import UUID

from flask import Blueprint, request

from app.services.statistics_service import StatisticsService
from app.services.stock_service import StockService
from app.utils.decorators import handle_request, require_auth, require_vendor_manager
from app.utils.vendor_resolvers import vendor_from_query


class StatisticsController:
    def __init__(self):
        self.blueprint = self._create_blueprint()
        self._register_routes()

    def _create_blueprint(self) -> Blueprint:
        return Blueprint("statistics_controller", __name__, url_prefix="/api/statistics")

    def _register_routes(self):
        bp = self.blueprint
        bp.add_url_rule("/summary", view_func=self.handle_summary, methods=["GET"])
        bp.add_url_rule("/stock", view_func=self.handle_stock, methods=["GET"])
        bp.add_url_rule("/stock-alerts", view_func=self.handle_stock_alerts, methods=["GET"])
        bp.add_url_rule("/sales-trend", view_func=self.handle_sales_trend, methods=["GET"])
        bp.add_url_rule("/popular-items", view_func=self.handle_popular_items, methods=["GET"])
        bp.add_url_rule("/user-spend", view_func=self.handle_user_spend, methods=["GET"])
        bp.add_url_rule("/vendor-trend", view_func=self.handle_vendor_trend, methods=["GET"])
        bp.add_url_rule("/depletion-rates", view_func=self.handle_depletion_rates, methods=["GET"])

    @require_auth
    @require_vendor_manager(vendor_from_query())
    @handle_request
    def handle_summary(self, db):
        vendor_id = _require_vendor_id()
        kpi = StatisticsService.get_kpi_summary(db, vendor_id)
        stock = StatisticsService.get_stock_summary(db, vendor_id)
        return {"data": {**kpi, **stock}}, 200

    @require_auth
    @require_vendor_manager(vendor_from_query())
    @handle_request
    def handle_stock(self, db):
        vendor_id = _require_vendor_id()
        category_id = request.args.get("category_id", type=int)
        items = StockService.get_stock_levels(db, vendor_id, category_id)
        return {"data": {"items": items}}, 200

    @require_auth
    @require_vendor_manager(vendor_from_query())
    @handle_request
    def handle_stock_alerts(self, db):
        vendor_id = _require_vendor_id()
        alerts = StatisticsService.get_stock_alerts(db, vendor_id)
        return {"data": {"alerts": alerts}}, 200

    @require_auth
    @require_vendor_manager(vendor_from_query())
    @handle_request
    def handle_sales_trend(self, db):
        vendor_id = _require_vendor_id()
        from_date, to_date = _resolve_dates(db, vendor_id)
        trend = StatisticsService.get_sales_trend(db, vendor_id, from_date, to_date)
        return {"data": trend}, 200

    @require_auth
    @require_vendor_manager(vendor_from_query())
    @handle_request
    def handle_popular_items(self, db):
        vendor_id = _require_vendor_id()
        from_date, to_date = _resolve_dates(db, vendor_id)
        items = StatisticsService.get_popular_items(db, vendor_id, from_date, to_date)
        return {"data": {"items": items}}, 200

    @require_auth
    @require_vendor_manager(vendor_from_query())
    @handle_request
    def handle_user_spend(self, db):
        vendor_id = _require_vendor_id()
        from_date, to_date = _resolve_dates(db, vendor_id)
        rows = StatisticsService.get_per_user_spend(db, vendor_id, from_date, to_date)
        return {"data": {"users": rows}}, 200

    @require_auth
    @require_vendor_manager(vendor_from_query())
    @handle_request
    def handle_vendor_trend(self, db):
        vendor_id = _require_vendor_id()
        from_date = _parse_date(request.args.get("from"))
        to_date = _parse_date(request.args.get("to"))
        trend = StatisticsService.get_vendor_trend(db, vendor_id, from_date, to_date)
        return {"data": {"trend": trend}}, 200

    @require_auth
    @require_vendor_manager(vendor_from_query())
    @handle_request
    def handle_depletion_rates(self, db):
        vendor_id = _require_vendor_id()
        from_date, to_date = _resolve_dates(db, vendor_id)
        rates = StatisticsService.get_depletion_rates(db, vendor_id, from_date, to_date)
        return {"data": {"rates": rates}}, 200


def _require_vendor_id() -> UUID:
    raw = request.args.get("vendor_id")
    if not raw:
        raise ValueError("vendor_id is required")
    try:
        return UUID(raw)
    except ValueError:
        raise ValueError("vendor_id must be a valid UUID")


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _resolve_dates(db, vendor_id) -> tuple[date | None, date | None]:
    preset = request.args.get("preset")
    if preset:
        return StatisticsService.resolve_date_preset(db, vendor_id, preset)
    return _parse_date(request.args.get("from")), _parse_date(request.args.get("to"))
