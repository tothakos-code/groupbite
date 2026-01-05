import logging
from datetime import date
from typing import Optional

from dateutil.relativedelta import relativedelta
from flask import session

from app.db.session import get_session
from app.entities.order import Order, OrderState
from app.entities.order_item import OrderItem
from app.event_manager import event_manager
from app.repositories.order_item_repository import OrderItemRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.user_basket_repository import UserBasketRepository
from app.repositories.vendor_repository import VendorRepository
from app.scheduler import reschedule_task
from app.services.mail_sender_service import EmailService
from app.services.user_basket_service import UserBasketService
from app.socketio_singleton import SocketioSingleton


class OrderService:

    def __init__(self, order_item_repository: OrderItemRepository, user_basket_service: UserBasketService):
        self.order_item_repo = order_item_repository
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
    def find_open_order_by_vendor(db, order_id, order_date):
        order_repo = OrderRepository(db)
        order = order_repo.find_open_order_by_date_for_a_vendor(order_id, order_date)
        if not order:
            logging.info(f"Order {order_id} not found")
            raise ValueError(f"Order {order_id} not found")
        return order

    @staticmethod
    def get_all_order(db, args) -> Optional[dict]:
        order_repo = OrderRepository(db)
        try:
            limit = int(args.get('limit'))
            page = int(args.get('page'))
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
        return  {
            "items": result,
            "page": page,
            "limit": limit,
            "total_count": total_count
        }

    @staticmethod
    def get_order_items(order: Order, user_filter=None):
        if user_filter is not None:
            if not isinstance(user_filter, (list, tuple, set)):
                user_filter = [user_filter]
            user_filter = [str(uid) for uid in user_filter]

        result = {}

        if order.state_id == OrderState.CLOSED:
            items_source = order.order_items
        else:
            items_source = order.items

        for item in items_source:
            user_id_str = str(item.user_id)

            if user_filter is not None and user_id_str not in user_filter:
                continue

            if user_id_str not in result:
                result[user_id_str] = {
                    "user_id": user_id_str,
                    "items": []
                }

            result[user_id_str]["username"] = item.user.username if item.user else "Unknown"

            if order.state_id == OrderState.CLOSED:
                item_data = {
                    "item_id": item.menu_item_id,
                    "size_id": item.size_id,
                    "item_name": item.item_name,
                    "size_name": item.size_label,
                    "price": item.unit_price,
                    "category": None,
                    "quantity": item.count,
                    "total_price": item.total_price
                }
            else:
                item_data = {
                    "item_id": item.item.id,
                    "size_id": item.size.id,
                    "item_name": item.item.name,
                    "size_name": item.size.name,
                    "price": item.size.price,
                    "category": item.item.category,
                    "quantity": item.count,
                    "total_price": item.size.price * item.count
                }

            result[user_id_str]["items"].append(item_data)

        return result

    def close_order(self, db, order_id):
        order_repo = OrderRepository(db)
        order = order_repo.get_by_id(order_id)
        logging.info(f"Manual order triggered by userID: {session.get("user_id")} for order {order.id}")
        trigger_data = {
            "order_id": order_id
        }
        event_manager.trigger_event("beforeClose@" + order.vendor.name, trigger_data)
        if order.state_id == OrderState.CLOSED:
            return {"msg": "Order is already closed"}, 400

        ok = self._change_state(db, order, OrderState.CLOSED)
        if not ok:
            logging.error(f"Order close error")

        order.order_fee = trigger_data["order_fee"] if "order_fee" in trigger_data else order.vendor.settings["transport_price"]["value"]

        event_manager.trigger_event("afterClose@" + order.vendor.name, trigger_data)
        logging.info(f"Order closed successfully")
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

    def add_to_basket(self, db, order_id, user_id, item_id, size_id):
        order_repo = OrderRepository(db)
        order = order_repo.get_by_id( order_id)
        if not order:
            return {"error": "Order not found"}, 400

        data = {
            "order_id": order_id,
            "user_id": user_id,
            "menu_item_id": item_id,
            "size_id": size_id
        }

        event_manager.trigger_event("beforeAdd@" + order.vendor.name, data)

        basket_item = self.user_basket_service.add_item(
            db,
            user_id,
            item_id,
            size_id,
            order_id
        )

        event_manager.trigger_event("afterAdd@" + order.vendor.name, data)

        return basket_item

    def remove_from_basket(self, db, order_id, user_id, item_id, size_id):
        order_repo = OrderRepository(db)
        order = order_repo.get_by_id( order_id)
        if not order:
            return {"error": "Order not found"}, 400

        data = {
            "order_id": order_id,
            "user_id": user_id,
            "menu_item_id": item_id,
            "size_id": size_id
        }

        event_manager.trigger_event("beforeRemove@" + order.vendor.name, data)

        basket_item = self.user_basket_service.remove_item(
            db,
            user_id,
            item_id,
            size_id,
            order_id
        )

        event_manager.trigger_event("afterRemove@" + order.vendor.name, data)

        return basket_item

    def copy_basket(self, db, order_id, user_id, src_user_id):
        order_repo = OrderRepository(db)
        user_basket_repo = UserBasketRepository(db)
        self.user_basket_service.clear_items(db, user_id, order_id)
        for item in user_basket_repo.find_user_basket(order_id, src_user_id):
            for i in range(0, item.count):
                try:
                    self.user_basket_service.add_item(db, user_id, str(item.menu_item_id), item.size_id, order_id)
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

            date_of_order = order.date_of_order.strftime("%Y-%m-%d")
            if date_of_order not in result:
                result[date_of_order] = {}

            result[date_of_order][order.id] = order.serialized
            result[date_of_order][order.id]["vendor"] = order.vendor.name

            sum = 0
            # TODO: integrate OrderItem, it already has total_price
            if order.state_id == OrderState.CLOSED:
                for item in order.order_items:
                    sum += item.total_price
            else:
                for item in order.items:
                    sum += item.size.price * item.count
            sum += order.order_fee
            result[date_of_order][order.id]["sum"] = sum


            result[date_of_order][order.id]["user_count"] = len(order_participants)

        return result


    def get_statistics(self, db):
        year_result, year_labels = self._last_12_month_statistics(db)
        week_result, week_labels = self._last_7_days_statistics(db)
        return {
            "year_data": {
                "data": year_result,
                "labels": year_labels
            },
            "week_data": {
                "data": week_result,
                "labels": week_labels
            }
        }

    def email_order(self, db, order_id):
        order_repo = OrderRepository(db)
        order = order_repo.get_by_id(order_id)
        logging.info(f"Manual email send triggered by userID: {session.get("user_id")} for order {order_id}")

        if not order:
            raise ValueError(f"Order {order_id} not found")

        if order.state_id == OrderState.CLOSED:
            raise ValueError(f"Order {order_id} is already closed, cannot send email")

        vendor = order.vendor

        task_id = f"{str(vendor.id)}-closed"
        try:
            # Cancel the scheduled task for this vendor (if exists)
            reschedule_task(task_id)
            logging.info(f"Scheduled task '{task_id}' rescheduled to next day due to manual trigger.")
        except KeyError:
            logging.info(f"Scheduled task '{task_id}' not found.")

        # Execute the email logic manually
        if self.email_ordering_wrapper(order=order, manual=True):
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
        last_7_days = [(today - relativedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
        last_7_days.reverse()

        vendors = vendor_repo.find_all_active()
        vendor_dict = {vendor.id: vendor.name for vendor in vendors}

        daily_data = order_repo.get_daily_sums(start_date, today, list(vendor_dict.keys()))

        daily_lookup = {}
        for row in daily_data:
            key = f"{row.vendor_id}-{row.date_of_order.strftime('%Y-%m-%d')}"
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
        start_date = today - relativedelta(months=11)  # 11 months ago + current month = 12 months

        # Generate month list
        last_12_months = [(today - relativedelta(months=i)).strftime("%Y-%m") for i in range(12)]
        last_12_months.reverse()

        vendors = vendor_repo.find_all_active()
        vendor_dict = {vendor.id: vendor.name for vendor in vendors}

        monthly_data = order_repo.get_monthly_sums(start_date, today, list(vendor_dict.keys()))

        monthly_lookup = {}
        for row in monthly_data:
            key = f"{row.vendor_id}-{int(row.year)}-{int(row.month):02d}"
            monthly_lookup[key] = row.monthly_sum

        result = {}
        for vendor_id, vendor_name in vendor_dict.items():
            result[vendor_name] = {"data": []}

            for month in last_12_months:
                year, month_num = month.split('-')
                lookup_key = f"{vendor_id}-{year}-{month_num}"
                monthly_sum = monthly_lookup.get(lookup_key, 0)
                result[vendor_name]["data"].append(monthly_sum)

        return result, last_12_months

    def _change_state(self, db, order, new_state, user_id=None) -> bool:
        order_repo = OrderRepository(db)
        # If changing FROM CLOSED state to any other state, delete existing order items
        if order.state_id == OrderState.CLOSED and new_state != OrderState.CLOSED:
            order_repo.delete_order_items(order)

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
        return True

    def _create_order_items_and_calculate_total(self, db, order):
        order_price = 0
        created_items = []

        try:
            # Create order items from basket items
            for basket_item in order.items:
                # Create OrderItem with snapshot data
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=basket_item.menu_item_id,
                    size_id=basket_item.size_id,
                    user_id=basket_item.user_id,
                    count=basket_item.count,
                    item_name=basket_item.item.name,
                    size_label=basket_item.size.name,
                    unit_price=basket_item.size.price,
                    total_price=basket_item.size.price * basket_item.count
                )

                self.order_item_repo.save(db, order_item)
                created_items.append(order_item)
                order_price += order_item.total_price

            # Add order fee to total price
            order_price += order.order_fee
            order.total_price = order_price

            # Flush to get any database errors before final commit
            # db.flush()
            return True

        except Exception as e:
            logging.exception("Error creating order items. "+ str(e))
            # Clean up any partially created items
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
    def send_in_mail(order):
        from app.entities.user_basket import UserBasket

        baskets = UserBasket.find_items_by_order(order.id)
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
        success = email_service.send_order(order, basket_sum)
        if not success:
            logging.error("Email could not be sent")
            return False

        logging.info(f"Order {order.id} sent in email!")
        return True

    def email_ordering_wrapper(self, order: Order, manual=False):
        logging.info("Manual email ordering running")
        from app.event_manager import event_manager

        if not order:
            logging.warning("Order not found")
            return False

        event_manager.trigger_event(
            "beforeClose@" + order.vendor.name, {"order_id": order.id}
        )
        email_min_user = order.vendor.get_setting_value("email_min_user")
        if manual or (
            order.vendor.get_setting_value("auto_email_order")
            and (email_min_user == 0 or email_min_user <= len(order.get_users()))
        ):
            order.change_state(OrderState.CLOSED)
            self.send_in_mail(order)

            event_manager.trigger_event(
                "afterClose@" + order.vendor.name, {"order_id": order.id}
            )

            from app.socketio_singleton import SocketioSingleton

            socketio = SocketioSingleton.get_instance()

            socketio.emit(
                "be_order_update",
                {"order": order.serialized},
                to=f"{order.vendor_id}@{order.date_of_order}",
            )
            return True
        else:
            logging.info("Minimum order requirements are not met")
            event_manager.trigger_event(
                "closeFailed@" + order.vendor.name, {"order_id": order.id}
            )
            return False

    @staticmethod
    def emit_update(data):
        with get_session() as db:
            order_repo = OrderRepository(db)
            order = order_repo.get_by_id(data["order_id"])
            socketio = SocketioSingleton.get_instance()
            socketio.emit(
                "be_order_update",
                {"basket": order.get_order_items()},
                to=f"{order.vendor_id}@{order.date_of_order}"
            )
            from app import VendorFactory
            vendor = VendorFactory.get_one_vendor_object(str(order.vendor_id))
            socketio.emit(
                "be_menu_update",
                {"menus": vendor.get_menus(str(order.date_of_order))},
                to=f"{order.vendor_id}@{order.date_of_order}"
            )