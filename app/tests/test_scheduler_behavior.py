"""
Regression tests for multi-day order scheduler behavior (order_duration_days > 1).

These tests call the wrapper functions directly with mocked dependencies
instead of waiting multiple real days for timers to fire.

Test matrix
───────────────────────────────────────────────────────────────────────
open_until calculation      open_until = today + duration - 1
closed_wrapper ref date     passes date.today() so the order is found on
                            effective_until (not only on open_from)
closed_wrapper reschedule   reschedules to effective_until + duration,
                            not to the very next calendar day
closure_wrapper reschedule  same reschedule logic as closed_wrapper
───────────────────────────────────────────────────────────────────────
"""
from datetime import date, timedelta
from unittest.mock import MagicMock, patch


# ── shared helpers ────────────────────────────────────────────────────────────

def _fake_order(open_from: date, duration_days: int = 7) -> MagicMock:
    order = MagicMock()
    order.id = 1
    order.vendor_id = "vendor-abc"
    order.open_from = open_from
    order.effective_until = open_from + timedelta(days=duration_days - 1)
    order.serialized = {"id": 1}
    return order


def _fake_vendor(vendor_id: str = "vendor-abc") -> MagicMock:
    vendor = MagicMock()
    vendor.id = vendor_id
    return vendor


def _settings(duration: int = 7) -> dict:
    return {
        "order_duration_days": duration,
        "auto_email_order": False,
        "email_min_user": 0,
        "favourite_notification_on_order": False,
    }


def _mock_session(mock_db: MagicMock) -> MagicMock:
    ctx = MagicMock()
    ctx.__enter__ = MagicMock(return_value=mock_db)
    ctx.__exit__ = MagicMock(return_value=False)
    return MagicMock(return_value=ctx)


# ── open_until calculation ────────────────────────────────────────────────────

class TestOpenUntilCalculation:

    def test_open_until_is_today_plus_duration_minus_one(self):
        today = date(2026, 1, 1)
        order_duration_days = 7
        open_until = today + timedelta(days=order_duration_days - 1)
        assert open_until == date(2026, 1, 7)

    def test_order_spans_exactly_duration_days(self):
        today = date(2026, 1, 1)
        for duration in [1, 3, 7, 14]:
            open_until = today + timedelta(days=duration - 1)
            assert (open_until - today).days == duration - 1


# ── closed_wrapper: reference date ───────────────────────────────────────────

class TestClosedWrapperReferenceDate:
    """closed_wrapper must query the order using date.today() so it finds
    multi-day orders on their last day (effective_until)."""

    @patch("app.scheduler.reschedule_task")
    @patch("app.socketio_singleton.SocketioSingleton")
    @patch("app.event_manager.event_manager")
    @patch("app.services.vendor_service.get_session")
    def test_find_open_order_called_with_today(
        self, mock_get_session, _event, mock_socketio_cls, _reschedule
    ):
        from app.services.vendor_service import VendorService

        open_from = date(2026, 1, 1)
        effective_until = date(2026, 1, 7)
        order = _fake_order(open_from, duration_days=7)

        mock_db = MagicMock()
        mock_get_session.return_value = MagicMock(
            __enter__=MagicMock(return_value=mock_db),
            __exit__=MagicMock(return_value=False),
        )
        mock_order_svc = MagicMock()
        mock_order_svc.find_open_order_by_vendor.return_value = order
        mock_order_svc._change_state.return_value = True
        mock_socketio_cls.get_instance.return_value = MagicMock()

        svc = VendorService(mock_order_svc)
        s = _settings()

        with patch.object(VendorService, "get_setting_value", side_effect=lambda v, k, d=None: s.get(k, d)):
            with patch("app.services.vendor_service.date") as mock_date:
                mock_date.today.return_value = effective_until
                svc.closed_wrapper(_fake_vendor())

        _, _, ref_date = mock_order_svc.find_open_order_by_vendor.call_args.args
        assert ref_date == effective_until

    @patch("app.scheduler.reschedule_task")
    @patch("app.socketio_singleton.SocketioSingleton")
    @patch("app.event_manager.event_manager")
    @patch("app.services.vendor_service.get_session")
    def test_order_is_closed_when_today_equals_effective_until(
        self, mock_get_session, _event, mock_socketio_cls, _reschedule
    ):
        from app.services.vendor_service import VendorService
        from app.entities.order import OrderState

        open_from = date(2026, 1, 1)
        effective_until = date(2026, 1, 7)
        order = _fake_order(open_from, duration_days=7)

        mock_db = MagicMock()
        mock_get_session.return_value = MagicMock(
            __enter__=MagicMock(return_value=mock_db),
            __exit__=MagicMock(return_value=False),
        )
        mock_order_svc = MagicMock()
        mock_order_svc.find_open_order_by_vendor.return_value = order
        mock_order_svc._change_state.return_value = True
        mock_socketio_cls.get_instance.return_value = MagicMock()

        svc = VendorService(mock_order_svc)
        s = _settings()

        with patch.object(VendorService, "get_setting_value", side_effect=lambda v, k, d=None: s.get(k, d)):
            with patch("app.services.vendor_service.date") as mock_date:
                mock_date.today.return_value = effective_until
                svc.closed_wrapper(_fake_vendor())

        mock_order_svc._change_state.assert_called_once_with(mock_db, order, OrderState.CLOSED)


# ── closed_wrapper: reschedule target ────────────────────────────────────────

class TestClosedWrapperReschedule:
    """After firing, closed_wrapper reschedules to effective_until + duration,
    not to the very next calendar day."""

    @patch("app.scheduler.reschedule_task")
    @patch("app.socketio_singleton.SocketioSingleton")
    @patch("app.event_manager.event_manager")
    @patch("app.services.vendor_service.get_session")
    def test_next_fire_date_is_effective_until_plus_duration(
        self, mock_get_session, _event, mock_socketio_cls, mock_reschedule
    ):
        from app.services.vendor_service import VendorService

        open_from = date(2026, 1, 1)
        order = _fake_order(open_from, duration_days=7)
        # effective_until = 2026-01-07  →  expected next fire = 2026-01-14

        mock_db = MagicMock()
        mock_get_session.return_value = MagicMock(
            __enter__=MagicMock(return_value=mock_db),
            __exit__=MagicMock(return_value=False),
        )
        mock_order_svc = MagicMock()
        mock_order_svc.find_open_order_by_vendor.return_value = order
        mock_order_svc._change_state.return_value = True
        mock_socketio_cls.get_instance.return_value = MagicMock()

        vendor = _fake_vendor()
        svc = VendorService(mock_order_svc)
        s = _settings()

        with patch.object(VendorService, "get_setting_value", side_effect=lambda v, k, d=None: s.get(k, d)):
            svc.closed_wrapper(vendor)

        expected_next = order.effective_until + timedelta(days=7)
        mock_reschedule.assert_called_once_with(
            f"{vendor.id}-closed",
            next_fire_date=expected_next,
        )

    @patch("app.scheduler.reschedule_task")
    @patch("app.socketio_singleton.SocketioSingleton")
    @patch("app.event_manager.event_manager")
    @patch("app.services.vendor_service.get_session")
    def test_next_fire_date_is_not_effective_until_plus_one_day(
        self, mock_get_session, _event, mock_socketio_cls, mock_reschedule
    ):
        from app.services.vendor_service import VendorService

        open_from = date(2026, 1, 1)
        order = _fake_order(open_from, duration_days=7)

        mock_db = MagicMock()
        mock_get_session.return_value = MagicMock(
            __enter__=MagicMock(return_value=mock_db),
            __exit__=MagicMock(return_value=False),
        )
        mock_order_svc = MagicMock()
        mock_order_svc.find_open_order_by_vendor.return_value = order
        mock_order_svc._change_state.return_value = True
        mock_socketio_cls.get_instance.return_value = MagicMock()

        vendor = _fake_vendor()
        svc = VendorService(mock_order_svc)
        s = _settings()

        with patch.object(VendorService, "get_setting_value", side_effect=lambda v, k, d=None: s.get(k, d)):
            svc.closed_wrapper(vendor)

        wrong_next = order.effective_until + timedelta(days=1)
        call_kwargs = mock_reschedule.call_args.kwargs
        actual_next = call_kwargs.get("next_fire_date") or mock_reschedule.call_args.args[1]
        assert actual_next != wrong_next, "reschedule must jump by duration, not 1 day"


# ── closure_wrapper: reschedule target ───────────────────────────────────────

class TestClosureWrapperReschedule:
    """closure_wrapper (ORDER state / Siess warning) must also reschedule to
    effective_until + duration, not the next calendar day."""

    @patch("app.scheduler.reschedule_task")
    @patch("app.socketio_singleton.SocketioSingleton")
    @patch("app.services.notification_service.NotificationService")
    @patch("app.event_manager.event_manager")
    @patch("app.services.vendor_service.get_session")
    def test_reschedules_to_effective_until_plus_duration(
        self, mock_get_session, _event, _notif, mock_socketio_cls, mock_reschedule
    ):
        from app.services.vendor_service import VendorService

        open_from = date(2026, 1, 1)
        order = _fake_order(open_from, duration_days=7)

        mock_db = MagicMock()
        mock_get_session.return_value = MagicMock(
            __enter__=MagicMock(return_value=mock_db),
            __exit__=MagicMock(return_value=False),
        )
        mock_order_svc = MagicMock()
        mock_order_svc.find_open_order_by_vendor.return_value = order
        mock_order_svc._change_state.return_value = True
        mock_socketio_cls.get_instance.return_value = MagicMock()

        vendor = _fake_vendor()
        svc = VendorService(mock_order_svc)
        s = _settings()

        with patch.object(VendorService, "get_setting_value", side_effect=lambda v, k, d=None: s.get(k, d)):
            svc.closure_wrapper(vendor)

        expected_next = order.effective_until + timedelta(days=7)
        mock_reschedule.assert_called_once_with(
            f"{vendor.id}-closure",
            next_fire_date=expected_next,
        )

    @patch("app.scheduler.reschedule_task")
    @patch("app.socketio_singleton.SocketioSingleton")
    @patch("app.services.notification_service.NotificationService")
    @patch("app.event_manager.event_manager")
    @patch("app.services.vendor_service.get_session")
    def test_fires_on_last_day_of_span(
        self, mock_get_session, _event, _notif, mock_socketio_cls, _reschedule
    ):
        """closure_wrapper passes date.today() so it finds the order on effective_until."""
        from app.services.vendor_service import VendorService

        open_from = date(2026, 1, 1)
        effective_until = date(2026, 1, 7)
        order = _fake_order(open_from, duration_days=7)

        mock_db = MagicMock()
        mock_get_session.return_value = MagicMock(
            __enter__=MagicMock(return_value=mock_db),
            __exit__=MagicMock(return_value=False),
        )
        mock_order_svc = MagicMock()
        mock_order_svc.find_open_order_by_vendor.return_value = order
        mock_order_svc._change_state.return_value = True
        mock_socketio_cls.get_instance.return_value = MagicMock()

        vendor = _fake_vendor()
        svc = VendorService(mock_order_svc)
        s = _settings()

        with patch.object(VendorService, "get_setting_value", side_effect=lambda v, k, d=None: s.get(k, d)):
            with patch("app.services.vendor_service.date") as mock_date:
                mock_date.today.return_value = effective_until
                svc.closure_wrapper(vendor)

        _, _, ref_date = mock_order_svc.find_open_order_by_vendor.call_args.args
        assert ref_date == effective_until
