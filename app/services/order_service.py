import logging
from datetime import date, timedelta
from typing import Optional

from dateutil.relativedelta import relativedelta
from flask import session

from app.db.session import get_session
from app.entities.order import Order, OrderState
from app.entities.order_item import OrderItem
from app.event_manager import event_manager
from app.repositories.basket_option_selection_repository import BasketOptionSelectionRepository
from app.repositories.menu_item_repository import MenuItemRepository
from app.repositories.order_item_repository import OrderItemRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.size_repository import SizeRepository
from app.repositories.user_basket_repository import UserBasketRepository
from app.repositories.user_repository import UserRepository
from app.repositories.vendor_repository import VendorRepository
from app.scheduler import reschedule_task
from app.services.bundle_engine import bundle_engine
from app.services.mail_sender_service import EmailService
from app.services.user_basket_service import UserBasketService
from app.socketio_singleton import SocketioSingleton


class OrderService:
    def __init__(
        self,
        user_basket_service: UserBasketService,
    ):
        self.user_basket_service = user_basket_service

    @staticmethod
    def get_order_by_id(db, order_id: int) -> Optional[Order]:
        order_repo = OrderRepository(db)
        order = order_repo.get_by_id(order_id)
        if not order:
            logging.info(f"Order {order_id} not found")
            raise ValueError(f"Order {order_id} not found")
        return order

    @staticmethod
    def find_open_order_by_vendor(db, vendor_id, reference_date=None):
        order_repo = OrderRepository(db)
        order = order_repo.find_open_order_for_vendor(vendor_id, reference_date)
        if not order:
            logging.info(f"Open order not found for vendor {vendor_id}")
            raise ValueError(f"Open order not found for vendor {vendor_id}")
        return order

    @staticmethod
    def get_all_order(db, args) -> Optional[dict]:
        order_repo = OrderRepository(db)
        try:
            limit = int(args.get("limit"))
            page = int(args.get("page"))
        except ValueError or TypeError:
            limit = 10
            page = 1
        offset = 0 if page is None else limit * (page - 1)
        # TODO: refactor find_all into one call
        orders = order_repo.find_all(limit, offset)
        total_count = len(order_repo.find_all())
        result = []
        for order in orders:
            result.append(order.serialized)
        return {
            "items": result,
            "page": page,
            "limit": limit,
            "total_count": total_count,
        }

    @staticmethod
    def get_order_items(order: Order, user_filter=None, db=None):
        if user_filter is not None:
            if not isinstance(user_filter, (list, tuple, set)):
                user_filter = [user_filter]
            user_filter = [str(uid) for uid in user_filter]

        result = {}

        if order.state_id == OrderState.CLOSED:
            for item in order.order_items:
                user_id_str = str(item.user_id)
                if user_filter is not None and user_id_str not in user_filter:
                    continue
                if user_id_str not in result:
                    result[user_id_str] = {"user_id": user_id_str, "items": []}
                result[user_id_str]["username"] = item.user.username if item.user else "Unknown"
                result[user_id_str]["items"].append({
                    "item_id": item.menu_item_id,
                    "size_id": item.size_id,
                    "item_name": item.item_name,
                    "size_name": item.size_label,
                    "price": item.unit_price,
                    "effective_price": item.unit_price,
                    "packaging_fee": item.packaging_fee,
                    "category": None,
                    "quantity": item.count,
                    "total_price": item.total_price,
                    "option_selections": [],
                    "bundle_discount": None,
                    "extras_summary": item.extras_summary,
                })
            return result

        # COLLECT / ORDER state — enrich with live option selections and bundle matches.
        matches = {}
        selections_index = {}
        if db is not None:
            try:
                matches = bundle_engine.compute_matches(db, order.id, order.vendor_id)
            except Exception:
                logging.warning("Bundle engine failed for order %s", order.id, exc_info=True)
            for sel in BasketOptionSelectionRepository(db).find_by_order_with_details(order.id):
                key = (str(sel.user_id), sel.menu_item_id, sel.size_id, sel.line_key)
                selections_index.setdefault(key, []).append(sel)

        for item in order.items:
            user_id_str = str(item.user_id)
            if user_filter is not None and user_id_str not in user_filter:
                continue
            if user_id_str not in result:
                result[user_id_str] = {"user_id": user_id_str, "items": []}
            result[user_id_str]["username"] = item.user.username if item.user else "Unknown"

            sel_key = (user_id_str, item.menu_item_id, item.size_id, item.line_key)
            selections = selections_index.get(sel_key, [])
            option_delta = sum(s.choice.price_delta for s in selections if s.choice)
            option_selections_data = [
                {
                    "choice_id": s.choice.id if s.choice else None,
                    "group": s.choice.group.name if s.choice and s.choice.group else None,
                    "choice": s.choice.name if s.choice else None,
                    "delta": s.choice.price_delta if s.choice else 0,
                }
                for s in selections
            ]

            base_price = item.size.price
            pkg_fee = item.item.effective_packaging_fee
            match = matches.get((user_id_str, item.menu_item_id, item.size_id))
            matched_units = match["matched_units"] if match else 0
            total_units = item.count

            option_choice_ids = [s.choice.id for s in selections if s.choice]

            def _make_item_data(qty, extra_delta, bundle_info):
                effective = base_price + option_delta + extra_delta + pkg_fee
                return {
                    "item_id": item.item.id,
                    "size_id": item.size.id,
                    "item_name": item.item.name,
                    "size_name": item.size.name,
                    "price": base_price,
                    "option_delta": option_delta,
                    "packaging_fee": pkg_fee,
                    "effective_price": effective,
                    "category_id": item.item.category_id,
                    "category": item.item.category_obj.name if item.item.category_obj else None,
                    "quantity": qty,
                    "total_price": effective * qty,
                    "option_selections": option_selections_data,
                    "option_choice_ids": option_choice_ids,
                    "bundle_discount": bundle_info,
                    "extras_summary": None,
                }

            if matched_units == 0:
                result[user_id_str]["items"].append(_make_item_data(total_units, 0, None))
            elif matched_units == total_units:
                bundle_info = {
                    "name": match["bundle_name"],
                    "bundle_id": match["bundle_id"],
                    "original_price": base_price + option_delta,
                    "applied_delta": match["applied_delta"],
                }
                result[user_id_str]["items"].append(
                    _make_item_data(total_units, match["applied_delta"], bundle_info)
                )
            else:
                # Partial match — emit two rows.
                bundle_info = {
                    "name": match["bundle_name"],
                    "bundle_id": match["bundle_id"],
                    "original_price": base_price + option_delta,
                    "applied_delta": match["applied_delta"],
                }
                result[user_id_str]["items"].append(
                    _make_item_data(matched_units, match["applied_delta"], bundle_info)
                )
                result[user_id_str]["items"].append(
                    _make_item_data(total_units - matched_units, 0, None)
                )

        return result

    @staticmethod
    def create_order_for_vendor(db, vendor, open_until=None, close_time=None, user_id=None):
        """
        Find-or-create an order for the vendor starting today.
        Returns (order, created: bool).
        close_time: datetime.time — if set, a one-shot timer will close the order at
                    that time on the open_until date (or today if open_until is None).
        Raises ValueError('open_until_before_today') or ValueError('overlapping_order').
        """
        from app.repositories.order_repository import OrderRepository
        from app.utils.vendor_settings import get_setting_value

        open_from = open_until if open_until is not None else date.today()

        if open_until is not None and open_until < date.today():
            raise ValueError("open_until_before_today")

        order_repo = OrderRepository(db)

        existing = order_repo.find_open_order_for_vendor(vendor.id, open_from)
        if existing:
            return existing, False

        effective_until = open_until or open_from
        if order_repo.has_overlapping_open_order(vendor.id, open_from, effective_until):
            raise ValueError("overlapping_order")

        order = order_repo.save(
            Order(
                vendor_id=vendor.id,
                open_from=open_from,
                open_until=open_until,
                close_time=close_time,
                order_fee=get_setting_value(vendor, "transport_price"),
                user_id=user_id,
            )
        )
        return order, True

    @staticmethod
    def delete_order(db, order_id: int):
        from app.repositories.user_basket_repository import UserBasketRepository
        order_repo = OrderRepository(db)
        user_basket_repo = UserBasketRepository(db)
        order = order_repo.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        if order.state_id == OrderState.CLOSED:
            raise ValueError("Closed orders cannot be deleted")
        if order.order_items:
            raise ValueError("Order has order items but is not closed — data inconsistency")
        if order.items and order.open_from >= date.today() - timedelta(weeks=1):
            raise ValueError("Cannot delete a non-empty order less than a week old")
        user_basket_repo.clear_order_items(order_id)
        db.flush()
        order_repo.delete(order)

    def close_order(self, db, order_id):
        order_repo = OrderRepository(db)
        order = order_repo.get_by_id(order_id)
        if not order:
            logging.info(f"Order {order_id} not found")
            raise Exception("order not found")
        logging.info(
            f"Manual order triggered by userID: {session.get('user_id')} for order {order.id}"
        )
        trigger_data = {"order_id": order_id, "order": order.serialized}
        event_manager.trigger_event("beforeClose@" + str(order.vendor_id), trigger_data)
        if order.state_id == OrderState.CLOSED:
            return {"msg": "Order is already closed"}, 400

        # beforeClose may have modified baskets in a separate session; expire so items reload
        db.expire(order)
        ok = self._change_state(db, order, OrderState.CLOSED)
        if not ok:
            logging.error("Order close error")
        from app.services.vendor_service import VendorService

        order.order_fee = (
            trigger_data["order_fee"]
            if "order_fee" in trigger_data
            else VendorService.get_setting_value(order.vendor, "transport_price")
        )
        order.ordered_by = UserRepository(db).get_by_id(session.get("user_id"))
        event_manager.trigger_event("afterClose@" + str(order.vendor_id), trigger_data)
        logging.info("Order closed successfully")
        return order

    def update_order(self, db, order_id, data) -> Order:
        order_repo = OrderRepository(db)
        order = order_repo.get_by_id(order_id)
        if not order:
            logging.info(f"Order {order_id} not found")
            raise Exception("order not found")

        new_state = OrderState(data["state_id"])

        if not self._change_state(db, order, new_state):
            raise ValueError()

        order.order_fee = data["order_fee"]
        return order

    def add_to_basket(self, db, order_id, user_id, item_id, size_id, option_choice_ids=None):
        order_repo = OrderRepository(db)
        user_repo = UserRepository(db)
        menu_item_repo = MenuItemRepository(db)
        size_repo = SizeRepository(db)
        order = order_repo.get_by_id(order_id)
        user = user_repo.get_by_id(user_id)
        item = menu_item_repo.get_by_id(item_id)
        size = size_repo.get_by_id(size_id)
        if not order:
            return {"error": "Order not found"}, 400

        data = {
            "order_id": order_id,
            "order": order.serialized,
            "user_id": user_id,
            "user": user.serialized,
            "menu_item_id": item_id,
            "item": item.serialized,
            "size_id": size_id,
            "size": size.serialized,
        }

        event_manager.trigger_event("beforeAdd@" + str(order.vendor_id), data)

        basket_item = self.user_basket_service.add_item(
            db, user_id, item_id, size_id, order_id, option_choice_ids=option_choice_ids
        )

        event_manager.trigger_event("afterAdd@" + str(order.vendor_id), data)

        return basket_item

    def remove_from_basket(self, db, order_id, user_id, item_id, size_id, option_choice_ids=None):
        order_repo = OrderRepository(db)
        user_repo = UserRepository(db)
        menu_item_repo = MenuItemRepository(db)
        size_repo = SizeRepository(db)
        order = order_repo.get_by_id(order_id)
        user = user_repo.get_by_id(user_id)
        item = menu_item_repo.get_by_id(item_id)
        size = size_repo.get_by_id(size_id)
        if not order:
            return {"error": "Order not found"}, 400

        data = {
            "order_id": order_id,
            "order": order.serialized,
            "user_id": user_id,
            "user": user.serialized,
            "menu_item_id": item_id,
            "item": item.serialized,
            "size_id": size_id,
            "size": size.serialized,
        }

        event_manager.trigger_event("beforeRemove@" + str(order.vendor_id), data)

        basket_item = self.user_basket_service.remove_item(
            db, user_id, item_id, size_id, order_id, option_choice_ids=option_choice_ids
        )

        event_manager.trigger_event("afterRemove@" + str(order.vendor_id), data)

        return basket_item

    def copy_basket(self, db, order_id, user_id, src_user_id):
        order_repo = OrderRepository(db)
        user_basket_repo = UserBasketRepository(db)
        bos_repo = BasketOptionSelectionRepository(db)

        self.user_basket_service.clear_items(db, user_id, order_id)

        for item in user_basket_repo.find_user_basket(order_id, src_user_id):
            src_selections = bos_repo.find_by_basket_entry(
                src_user_id, order_id, item.menu_item_id, item.size_id, item.line_key
            )
            src_choice_ids = [sel.option_choice_id for sel in src_selections]

            for i in range(item.count):
                try:
                    self.user_basket_service.add_item(
                        db, user_id, str(item.menu_item_id), item.size_id, order_id,
                        option_choice_ids=src_choice_ids,
                        skip_validation=True,
                    )
                except ValueError as e:
                    logging.error(e)
                    continue

        order = order_repo.get_by_id(order_id)
        return order

    @staticmethod
    def get_history(db, date_from, date_to):
        order_repo = OrderRepository(db)
        result = {}
        for order in order_repo.find_orders_between_dates(date_from, date_to):
            order_participants = order_repo.find_order_participants(order)
            if len(order_participants) == 0:
                continue

            open_from = order.open_from.strftime("%Y-%m-%d")
            if open_from not in result:
                result[open_from] = {}

            result[open_from][order.id] = order.serialized
            result[open_from][order.id]["vendor"] = order.vendor.name

            sum = 0
            # TODO: integrate OrderItem, it already has total_price
            if order.state_id == OrderState.CLOSED:
                for item in order.order_items:
                    sum += item.total_price
            else:
                for item in order.items:
                    sum += item.size.price * item.count
            sum += order.order_fee
            result[open_from][order.id]["sum"] = sum

            result[open_from][order.id]["user_count"] = len(order_participants)
            result[open_from][order.id]["ordered"] = any(
                str(user.id) == session.get("user_id") for user in order_participants
            )

        return result

    def get_statistics(self, db):
        year_result, year_labels = self._last_12_month_statistics(db)
        week_result, week_labels = self._last_7_days_statistics(db)
        return {
            "year_data": {"data": year_result, "labels": year_labels},
            "week_data": {"data": week_result, "labels": week_labels},
        }

    def email_order(self, db, order_id, extra_cc: list = []):
        order_repo = OrderRepository(db)
        order = order_repo.get_by_id(order_id)
        logging.info(
            f"Manual email send triggered by userID: {session.get('user_id')} for order {order_id}"
        )

        if not order:
            raise ValueError(f"Order {order_id} not found")

        if order.state_id == OrderState.CLOSED:
            raise ValueError(f"Order {order_id} is already closed, cannot send email")

        vendor = order.vendor
        order.ordered_by = UserRepository(db).get_by_id(session.get("user_id"))
        task_id = f"{str(vendor.id)}-closed"
        try:
            # Cancel the scheduled task for this vendor (if exists)
            reschedule_task(task_id)
            logging.info(
                f"Scheduled task '{task_id}' rescheduled to next day due to manual trigger."
            )
        except KeyError:
            logging.info(f"Scheduled task '{task_id}' not found.")

        # Execute the email logic manually
        if self.email_ordering_wrapper(order=order, manual=True, extra_cc=extra_cc):
            return {"msg": "Email sent and order closed manually"}, 200
        else:
            raise ValueError("Something went wrong during the action")

    @staticmethod
    def _last_7_days_statistics(db):
        order_repo = OrderRepository(db)
        vendor_repo = VendorRepository(db)

        today = date.today()
        start_date = today - relativedelta(days=6)  # 6 days ago + today = 7 days

        # Generate day list
        last_7_days = [
            (today - relativedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)
        ]
        last_7_days.reverse()

        vendors = vendor_repo.find_all_active()
        vendor_dict = {vendor.id: vendor.name for vendor in vendors}

        daily_data = order_repo.get_daily_sums(
            start_date, today, list(vendor_dict.keys())
        )

        daily_lookup = {}
        for row in daily_data:
            key = f"{row.vendor_id}-{row.open_from.strftime('%Y-%m-%d')}"
            daily_lookup[key] = row.daily_sum

        result = {}
        for vendor_id, vendor_name in vendor_dict.items():
            result[vendor_name] = {"data": []}

            for day in last_7_days:
                lookup_key = f"{vendor_id}-{day}"
                daily_sum = daily_lookup.get(lookup_key, 0)
                result[vendor_name]["data"].append(daily_sum)

        return result, last_7_days

    @staticmethod
    def _last_12_month_statistics(db):
        order_repo = OrderRepository(db)
        vendor_repo = VendorRepository(db)

        today = date.today()
        start_date = today - relativedelta(
            months=11
        )  # 11 months ago + current month = 12 months

        # Generate month list
        last_12_months = [
            (today - relativedelta(months=i)).strftime("%Y-%m") for i in range(12)
        ]
        last_12_months.reverse()

        vendors = vendor_repo.find_all_active()
        vendor_dict = {vendor.id: vendor.name for vendor in vendors}

        monthly_data = order_repo.get_monthly_sums(
            start_date, today, list(vendor_dict.keys())
        )

        monthly_lookup = {}
        for row in monthly_data:
            key = f"{row.vendor_id}-{int(row.year)}-{int(row.month):02d}"
            monthly_lookup[key] = row.monthly_sum

        result = {}
        for vendor_id, vendor_name in vendor_dict.items():
            result[vendor_name] = {"data": []}

            for month in last_12_months:
                year, month_num = month.split("-")
                lookup_key = f"{vendor_id}-{year}-{month_num}"
                monthly_sum = monthly_lookup.get(lookup_key, 0)
                result[vendor_name]["data"].append(monthly_sum)

        return result, last_12_months

    def _change_state(self, db, order, new_state, user_id=None) -> bool:
        order_item_repo = OrderItemRepository(db)
        # If changing FROM CLOSED state to any other state, delete existing order items
        if order.state_id == OrderState.CLOSED and new_state != OrderState.CLOSED:
            order_item_repo.delete_order_items(order)

        old_state = order.state_id
        order.state_id = new_state
        if user_id:
            order.order_by = user_id

        # If changing TO CLOSED state, create order items and calculate total
        if new_state == OrderState.CLOSED and old_state != OrderState.CLOSED:
            success = self._create_order_items_and_calculate_total(db, order)
            if not success:
                order.state_id = old_state
                return False
            from app.services.option_group_service import OptionGroupService
            OptionGroupService.cleanup_inactive(db, order.vendor_id)
        return True

    def _create_order_items_and_calculate_total(self, db, order):
        order_price = 0
        created_items = []

        try:
            matches = bundle_engine.compute_matches(db, order.id, order.vendor_id)

            bos_repo = BasketOptionSelectionRepository(db)
            all_selections = bos_repo.find_by_order_with_details(order.id)
            selections_index = {}
            for sel in all_selections:
                key = (str(sel.user_id), sel.menu_item_id, sel.size_id, sel.line_key)
                selections_index.setdefault(key, []).append(sel)

            order_item_repo = OrderItemRepository(db)

            for basket_item in order.items:
                user_id_str = str(basket_item.user_id)
                sel_key = (user_id_str, basket_item.menu_item_id, basket_item.size_id, basket_item.line_key)
                selections = selections_index.get(sel_key, [])
                option_delta = sum(s.choice.price_delta for s in selections if s.choice)

                options_summary = [
                    {
                        "group": s.choice.group.name if s.choice and s.choice.group else None,
                        "choice": s.choice.name if s.choice else None,
                        "delta": s.choice.price_delta if s.choice else 0,
                    }
                    for s in selections
                ]

                base_price = basket_item.size.price
                pkg_fee = basket_item.item.effective_packaging_fee
                price_with_options = base_price + option_delta
                match = matches.get((user_id_str, basket_item.menu_item_id, basket_item.size_id))
                matched_units = match["matched_units"] if match else 0
                total_units = basket_item.count

                def _make_order_item(count, unit_price, bundle_match):
                    bundle_summary = None
                    if bundle_match:
                        bundle_summary = {
                            "name": bundle_match["bundle_name"],
                            "original_price": price_with_options,
                            "applied_delta": bundle_match["applied_delta"],
                        }
                    extras = {}
                    if options_summary:
                        extras["options"] = options_summary
                    if bundle_summary:
                        extras["bundle"] = bundle_summary
                    return OrderItem(
                        order_id=order.id,
                        menu_item_id=basket_item.menu_item_id,
                        size_id=basket_item.size_id,
                        user_id=basket_item.user_id,
                        count=count,
                        item_name=basket_item.item.name,
                        size_label=basket_item.size.name,
                        unit_price=unit_price,
                        total_price=unit_price * count,
                        packaging_fee=pkg_fee,
                        extras_summary=extras if extras else None,
                    )

                if matched_units == 0:
                    items_to_save = [_make_order_item(total_units, price_with_options + pkg_fee, None)]
                elif matched_units == total_units:
                    discounted_price = price_with_options + match["applied_delta"]
                    items_to_save = [_make_order_item(total_units, discounted_price + pkg_fee, match)]
                else:
                    discounted_price = price_with_options + match["applied_delta"]
                    items_to_save = [
                        _make_order_item(matched_units, discounted_price + pkg_fee, match),
                        _make_order_item(total_units - matched_units, price_with_options + pkg_fee, None),
                    ]

                for order_item in items_to_save:
                    order_item_repo.save(order_item)
                    created_items.append(order_item)
                    order_price += order_item.total_price

            order_price += order.order_fee
            order.total_price = order_price
            return True

        except Exception as e:
            logging.exception("Error creating order items. " + str(e))
            for item in created_items:
                db.expunge(item)
            return False

    @staticmethod
    def update_order_fee(db, order_id, new_fee):
        order_repo = OrderRepository(db)
        order = order_repo.get_by_id(order_id)
        order.order_fee = new_fee
        return order

    @staticmethod
    def send_in_mail(order, extra_cc: list = []):
        with get_session() as db:
            baskets = UserBasketRepository(db).find_items_by_order(order.id)

        if len(baskets) == 0:
            logging.warning("The order is empty, email not sent")
            return False

        basket_sum = {}
        for item in baskets:
            if item.menu_item_id in basket_sum:
                basket_sum[item.menu_item_id]["quantity"] += item.count
            else:
                basket_sum[item.menu_item_id] = {
                    **item.basket_format,
                    "quantity": item.count,
                }

        email_service = EmailService()
        success = email_service.send_order(order, basket_sum, extra_cc=extra_cc)
        if not success:
            logging.error("Email could not be sent")
            return False

        logging.info(f"Order {order.id} sent in email!")
        return True

    def email_ordering_wrapper(self, order: Order, manual=False, extra_cc: list = []):
        logging.info("Manual email ordering running")
        from app.event_manager import event_manager
        from app.services.vendor_service import VendorService

        if not order:
            logging.warning("Order not found")
            return False

        event_manager.trigger_event(
            "beforeClose@" + str(order.vendor_id),
            {"order_id": order.id, "order": order.serialized},
        )
        email_min_user = VendorService.get_setting_value(order.vendor, "email_min_user")
        with get_session() as db:
            order_user_count = len(OrderRepository(db).find_order_participants(order))
            if manual or (
                VendorService.get_setting_value(order.vendor, "auto_email_order")
                and (email_min_user == 0 or email_min_user <= order_user_count)
            ):
                self._change_state(db, order, OrderState.CLOSED)
                self.send_in_mail(order, extra_cc=extra_cc)

                event_manager.trigger_event(
                    "afterClose@" + str(order.vendor_id),
                    {"order_id": order.id, "order": order.serialized},
                )

                from app.socketio_singleton import SocketioSingleton

                socketio = SocketioSingleton.get_instance()

                socketio.emit(
                    "be_order_update",
                    {"order": order.serialized},
                    to=f"{order.vendor_id}@{order.open_from}",
                )
                return True
            else:
                logging.info("Minimum order requirements are not met")
                event_manager.trigger_event(
                    "closeFailed@" + str(order.vendor_id),
                    {"order_id": order.id, "order": order.serialized},
                )
                return False

    @staticmethod
    def restore_adhoc_close_timers():
        """Called on startup to re-schedule one-shot close timers for open orders with close_time set."""
        from datetime import datetime as _dt
        from app.scheduler import schedule_once
        with get_session() as db:
            order_repo = OrderRepository(db)
            orders = order_repo.find_open_orders_with_close_time()
            for order in orders:
                target_dt = _dt.combine(order.effective_until, order.close_time)
                task_id = f"{order.vendor_id}-adhoc-close-{order.id}"
                schedule_once(task_id, target_dt, _adhoc_close_for_vendor, str(order.vendor_id))

    @staticmethod
    def emit_update(data):
        with get_session() as db:
            order_repo = OrderRepository(db)
            order = order_repo.get_by_id(data["order_id"])
            socketio = SocketioSingleton.get_instance()
            socketio.emit(
                "be_order_update",
                {"basket": OrderService.get_order_items(order, db=db)},
                to=f"{order.vendor_id}@{order.open_from}",
            )
            from app.services.vendor_service import VendorService

            menus = VendorService.get_menu_items(
                db, order.vendor_id, str(order.open_from)
            )
            socketio.emit(
                "be_menu_update",
                {"menus": menus},
                to=f"{order.vendor_id}@{order.open_from}",
            )


def _adhoc_close_for_vendor(vendor_id_str: str):
    """One-shot timer callback: closes the current open order for a vendor."""
    from app.services.vendor_service import VendorService

    with get_session() as db:
        vendor = VendorRepository(db).get_by_id(vendor_id_str)
        if not vendor:
            return

    service = VendorService(OrderService(UserBasketService()))
    service.closed_wrapper(vendor)
