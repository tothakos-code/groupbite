import logging
import re
from datetime import datetime, timedelta
from collections import Counter

from app.socketio_singleton import SocketioSingleton

socketio = SocketioSingleton.get_instance()
from flask import request, session, current_app

from app.entities.order import Order
from app.entities.user import User
from app.entities.user_basket import UserBasket
from app.repositories.user_repository import UserRepository


class UserService:

    @staticmethod
    def login(db, user_id):
        user_repo = UserRepository(db)
        if user_id:
            user = user_repo.get_by_id(user_id)
            if user:
                current_app.session_interface.regenerate(session)
                session.modified = True
                logging.info(f"User already {user.username} logged in!")
                return user

        username = request.json["username"]
        user_to_login = user_repo.get_by_username(username)
        if not user_to_login:
            logging.error(f"Error during login: {username} user does not exist, cannot log in.")
            raise ValueError(f"{username} felhasználó nem létezik!")
        session["user_id"] = user_to_login.id

        logging.info(f"User {user_to_login.username} logged in!")
        return user_to_login

    @staticmethod
    def logout(user_id):
        if user_id:
            session.clear()
            return { "msg": "Logged out successfully" }, 200
        else:
            logging.warning("Logout attempt without a user logged in.")
            raise (ValueError("No user is logged in."))

    def register(self, db, email, username):
        user_repo = UserRepository(db)
        is_username_valid, username_error = self.is_username_valid(db, username)
        is_email_valid, email_error = self.is_email_valid(db, email)

        if not is_username_valid:
            return { "error": username_error }

        if not is_email_valid:
            return { "error": email_error }
        user = User(username=username, email=email, settings={}, password="")
        user_repo.save(user)
        logging.info(f"User {user.username} created!")

        session["user_id"] = user.id
        session.permanent = True

        return user

    @staticmethod
    def check_session(db, user_id):
        user_repo = UserRepository(db)
        if user_id:
            user = user_repo.get_by_id(user_id)
            current_app.session_interface.regenerate(session)
            session.modified = True
            logging.info(f"User already {user.username} got a session!")
            return user
        else:
            raise ValueError(f"{user_id} nincs bejelentkezve!")

    @staticmethod
    def get_users(db, args):
        user_repo = UserRepository(db)
        try:
            limit = int(args.get('limit'))
            page = int(args.get('page'))
        except ValueError:
            limit = 10
            page = 1
        except TypeError:
            limit = 10
            page = 1
        offset = 0 if page is None else limit * (page - 1)
        users = user_repo.find_all(limit, offset)
        total_count = len(user_repo.find_all())
        result = []
        for user in users:
            result.append(user.serialized)
        return {
            "items": result,
            "page": page,
            "limit": limit,
            "total_count": total_count
        }

    def update_user(self, db, user_id, args ):
        user_repo = UserRepository(db)
        user_to_update = user_repo.get_by_id(user_id)

        if "username" in args:
            is_username_valid, error = self.is_username_valid(db, args["username"])
            if is_username_valid:
                user_to_update.username = args["username"]
                logging.info("Updated User: " + str(args["id"]))
            else:
                logging.info("Invalid user update: " + error)
                raise ValueError(error)

        if "username" in args:
            logging.info("Updating username in rooms")
            # Updating the username in every basket(room) a user is in
            for room_name,room in socketio.server.manager.rooms["/"].items():
                if room_name is not None and "@" in room_name:

                    vendor, date = room_name.split("@")
                    # TODO: check if user has items in that order, and only update them
                    order = Order.find_order_by_date_for_a_vendor(vendor, date)
                    socketio.emit(
                        "be_order_update", {
                            "basket": order.get_order_items()
                        },
                        to=room_name
                    )

        return user_to_update

    @staticmethod
    def is_username_valid(db, username):
        user_repo = UserRepository(db)
        invalid_usernames = [
            "null",
            "None",
            None,
            "undefined",
            ""
        ]
        if username in invalid_usernames:
            return False, "Ez nem lehet a neved: " + username

        invalid_characters = ["'", '"', "=", ",", ".", "&", "@", "#", "<", ">", "(", ")","[", "]", "{", "}", "%", ";", "*", "`"]
        for char in invalid_characters:
            if char in username:
                return False, "Tiltott karakter a felhasználónévben: " + char

        if user_repo.get_by_username(username):
            return False, "Ez a felhasználónév már foglalt"

        if len(username) > 50:
            return False, "Felhasználónév túl hosszú, válassz rövidebbet"

        return True, ""

    @staticmethod
    def is_email_valid(db, email):
        user_repo = UserRepository(db)
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
            return False, "Helytelen email formátum"

        if user_repo.get_by_email(email):
            return False, "Ez az email cím már foglalt"

        return True, ""

    # TODO: Move to UserBasket service
    @staticmethod
    def get_user_history(db, user_id, args):
        try:
            limit = int(args.get('limit'))
            page = int(args.get('page'))
        except (ValueError, TypeError):
            limit = 10
            page = 1

        search = args.get('search')
        vendor_id = args.get('vendor_id')
        date_from = args.get('date_from')
        date_to = args.get('date_to')
        offset = 0 if page is None else limit * (page - 1)

        user_items = UserBasket.find_user_orders(user_id, limit, offset, search, vendor_id, date_from, date_to)
        all_items = UserBasket.find_user_orders(user_id, None, 0, search, vendor_id, date_from, date_to)


        vendors = UserBasket.find_user_order_vendors(user_id)
        vendors_list = [{"id": vendor.id, "title": vendor.name} for vendor in vendors]

        all_order_ids = list(set(item.order_id for item in user_items))
        order_user_counts = UserBasket.get_user_counts_batch(all_order_ids)

        # Build orders dictionary
        orders_dict = {}
        for item in user_items:
            order_id = item.order_id
            if order_id not in orders_dict:
                order_participants_count = order_user_counts.get(order_id, 1)
                user_order_fee = item.order.order_fee / order_participants_count if order_participants_count > 0 else 0

                orders_dict[order_id] = {
                    "id": item.order.id,
                    "vendor": {"name": item.order.vendor.name},
                    "state_id": str(item.order.state_id),
                    "date_of_order": item.order.date_of_order.strftime("%Y-%m-%d"),
                    "order_time": item.order.order_time.isoformat() if item.order.order_time else None,
                    "order_fee": user_order_fee,
                    "total_price": 0,
                    "order_items": []
                }

            orders_dict[order_id]["order_items"].append({
                "id": item.menu_item_id,
                "item_name": item.item_name,
                "size_label": item.size_label,
                "count": item.count,
                "unit_price": item.unit_price,
                "total_price": item.total_price
            })
            orders_dict[order_id]["total_price"] += item.total_price


        # Add order fees to total prices
        for order_data in orders_dict.values():
            order_data["total_price"] += order_data["order_fee"]


        orders_list = list(orders_dict.values())
        orders_list.sort(key=lambda x: x["date_of_order"], reverse=True)

        unique_orders = set(item.order.id for item in all_items)
        total_orders = len(unique_orders)

        total_user_spending = sum(item.total_price for item in all_items)
        processed_orders = set()

        all_order_ids_for_total = list(unique_orders)
        all_order_user_counts = UserBasket.get_user_counts_batch(all_order_ids_for_total)

        for item in all_items:
            if item.order.id not in processed_orders:
                order_participants_count = all_order_user_counts.get(item.order.id, 1)
                user_order_fee = item.order.order_fee / order_participants_count if order_participants_count > 0 else 0
                total_user_spending += user_order_fee
                processed_orders.add(item.order.id)
        return {
                "items": orders_list,
                "vendors": vendors_list,
                "page": page,
                "limit": limit,
                "total_count": total_orders,
                "total_sum": total_user_spending
            }

    # TODO: move to UserBasket service
    @staticmethod
    def get_user_statistics(user_id):
        try:
            all_user_items = UserBasket.find_user_orders(user_id)

            if not all_user_items:
                return {
                    "totalOrders": 0,
                    "totalSpent": 0,
                    "totalItems": 0,
                    "uniqueVendors": 0,
                    "averageOrderValue": 0,
                    "favoriteVendor": None,
                    "favoriteItem": None,
                    "thisMonthSpent": 0,
                    "thisWeekSpent": 0,
                    "ordersThisMonth": 0,
                    "insights": []
                }

            # Basic calculations
            unique_orders = set()
            vendors = []
            items = []
            total_spent = 0
            total_items_count = 0

            # Time-based tracking
            now = datetime.now()
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            start_of_week = now - timedelta(days=now.weekday())
            start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

            this_month_spent = 0
            this_week_spent = 0
            orders_this_month = set()

            processed_order_fees = set()

            # Process each item
            for item in all_user_items:
                # Track unique orders
                order_id = item.order.id
                unique_orders.add(order_id)

                # Track vendors
                vendors.append(item.order.vendor.name)

                # Track items
                items.append(item.item_name)

                # Calculate item cost

                total_spent += item.total_price
                total_items_count += item.count

                # Add user's share of order fee (only once per order)
                if order_id not in processed_order_fees:
                    order_participants = UserBasket.user_count(order_id)
                    user_fee_share = item.order.order_fee / order_participants if order_participants > 0 else 0
                    total_spent += user_fee_share
                    processed_order_fees.add(order_id)

                # Time-based calculations
                order_date = item.order.date_of_order
                if isinstance(order_date, str):
                    order_date = datetime.strptime(order_date, "%Y-%m-%d").date()

                order_datetime = datetime.combine(order_date, datetime.min.time())

                if order_datetime >= start_of_month:
                    this_month_spent += item.total_price
                    orders_this_month.add(order_id)

                    # Add fee share for this month (only once per order)
                    if order_id not in processed_order_fees:
                        order_participants = UserBasket.user_count(order_id)
                        user_fee_share = item.order.order_fee / order_participants if order_participants > 0 else 0
                        this_month_spent += user_fee_share

                if order_datetime >= start_of_week:
                    this_week_spent += item.total_price

            # Calculate derived statistics
            total_orders = len(unique_orders)
            unique_vendors_count = len(set(vendors))
            average_order_value = total_spent / total_orders if total_orders > 0 else 0

            # Find favorite vendor
            vendor_counts = Counter(vendors)
            favorite_vendor = {
                "name": vendor_counts.most_common(1)[0][0],
                "count": vendor_counts.most_common(1)[0][1]
            } if vendor_counts else None

            # Find favorite item
            item_counts = Counter(items)
            favorite_item = {
                "name": item_counts.most_common(1)[0][0],
                "count": item_counts.most_common(1)[0][1]
            } if item_counts else None

            return {
                    "totalOrders": total_orders,
                    "totalSpent": total_spent,
                    "totalItems": total_items_count,
                    "uniqueVendors": unique_vendors_count,
                    "averageOrderValue": average_order_value,
                    "favoriteVendor": favorite_vendor,
                    "favoriteItem": favorite_item,
                    "thisMonthSpent": this_month_spent,
                    "thisWeekSpent": this_week_spent,
                    "ordersThisMonth": len(orders_this_month),
            }

        except Exception as e:
            print(f"Error calculating user statistics: {str(e)}")
            raise ValueError("Failed to calculate statistics")

    # TODO: Move to OrderService
    @staticmethod
    def get_user_spending_trends(user_id):
        try:
            months = 3
            # Calculate date range
            end_date = datetime.now().date()
            start_date = end_date.replace(month=end_date.month - months + 1) if end_date.month > months else \
                        end_date.replace(year=end_date.year - 1, month=end_date.month + 12 - months + 1)

            # Get user items within date range
            user_items = Order.find_user_order_dates_between(
                user_id,
                start_date,
                end_date
            )

            # Group by month
            monthly_spending = {}
            processed_order_fees = {}

            for item in user_items:
                order_date = item.order.date_of_order
                if isinstance(order_date, str):
                    order_date = datetime.strptime(order_date, "%Y-%m-%d").date()

                month_key = f"{order_date.year}-{order_date.month:02d}"

                if month_key not in monthly_spending:
                    monthly_spending[month_key] = 0
                    processed_order_fees[month_key] = set()

                # Add item cost
                item_cost = item.size.price * item.count
                monthly_spending[month_key] += item_cost

                # Add user's share of order fee (only once per order per month)
                order_id = item.order.id
                if order_id not in processed_order_fees[month_key]:
                    order_participants = UserBasket.user_count(order_id)
                    user_fee_share = item.order.order_fee / order_participants if order_participants > 0 else 0
                    monthly_spending[month_key] += user_fee_share
                    processed_order_fees[month_key].add(order_id)

            # Convert to list format for charting
            trends = []
            for month, spending in sorted(monthly_spending.items()):
                trends.append({
                    "month": month,
                    "spending": int(spending)  # Convert to cents
                })

            return trends
        except Exception as e:
            print(f"Error calculating spending trends: {str(e)}")
            raise ValueError("Failed to calculate trends")

    # TODO: Move to UserBasketService?
    @staticmethod
    def get_user_vendor_breakdown(db, user_id):
        user_repo = UserRepository(db)
        try:
            all_user_items = UserBasket.find_user_orders(user_id)

            vendor_spending = {}
            processed_order_fees = {}

            for item in all_user_items:
                vendor_name = item.order.vendor.name

                if vendor_name not in vendor_spending:
                    vendor_spending[vendor_name] = 0
                    processed_order_fees[vendor_name] = set()

                # Add item cost
                item_cost = item.size.price * item.count
                vendor_spending[vendor_name] += item_cost

                # Add user's share of order fee (only once per order per vendor)
                order_id = item.order.id
                if order_id not in processed_order_fees[vendor_name]:
                    order_participants = UserBasket.user_count(order_id)
                    user_fee_share = item.order.order_fee / order_participants if order_participants > 0 else 0
                    vendor_spending[vendor_name] += user_fee_share
                    processed_order_fees[vendor_name].add(order_id)

            # Convert to list and sort by spending
            breakdown = [
                {
                    "vendor": vendor,
                    "spending": int(spending * 100),  # Convert to cents
                    "percentage": round((spending / sum(vendor_spending.values())) * 100, 1) if vendor_spending else 0
                }
                for vendor, spending in vendor_spending.items()
            ]

            breakdown.sort(key=lambda x: x["spending"], reverse=True)

            return breakdown

        except Exception as e:
            print(f"Error calculating vendor breakdown: {str(e)}")
            raise ValueError("Failed to calculate breakdown")