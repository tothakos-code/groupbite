from flask import Blueprint, request, session, current_app
from flask_socketio import rooms
from sqlalchemy import func, cast, update
from datetime import datetime, timedelta
from collections import Counter
import logging
import re
from app.controllers import user_blueprint
from app.socketio_singleton import SocketioSingleton
from app.entities import Session
from app.entities.user import User
from app.entities.order import Order
from app.entities.user_basket import UserBasket
from app.utils.decorators import validate_url_params, require_auth, require_admin
from app.utils.validators import IDSchema


socketio = SocketioSingleton.get_instance()

@user_blueprint.route("/login", methods=["POST"])
def handle_user_login():
    user_id = session.get('user_id')
    if user_id:
        user_to_login = User.get_one_by_id(user_id)
        current_app.session_interface.regenerate(session)
        session.modified = True
        logging.info(f"User already {user_to_login.username} logged in!")
        return { "data": user_to_login.serialized }, 200

    username = request.json["username"]
    user_to_login = User.get_one_by_username(username)
    if not user_to_login:
        logging.error(f"Error during login: {username} user does not excist, cannot log in.")
        return { "error": f"{username} felhasználó nem létezik!" }


    session["user_id"] = user_to_login.id

    logging.info(f"User {user_to_login.username} logged in!")
    return { "data": user_to_login.serialized }, 200

@require_auth
@user_blueprint.route("/logout", methods=["POST"])
def handle_user_logout():
    user_id = session.get('user_id')
    if user_id:
        session.clear()
        return { "msg": "Logged out successfully" }, 200
    else:
        logging.warning("Logout attempt without a user logged in.")
        return { "error": "No user is logged in." }, 400


@user_blueprint.route("/checkSession", methods=["GET"])
def handle_user_check_session():
    user_id = session.get('user_id')
    if user_id:
        user_to_login = User.get_one_by_id(user_id)
        current_app.session_interface.regenerate(session)
        session.modified = True
        logging.info(f"User already {user_to_login.username} got a session!")
        return { "data": user_to_login.serialized }, 200
    else:
        return { "error": f"{user_id} nincs bejelentkezve!" }, 200

@user_blueprint.route("/reminder", methods=["GET"])
def handle_reminder():
    email = request.args.get('email')
    if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
        return { "error": "Helytelen email formátum" }, 200

    user = User.get_one_by_email(email)
    if user:
        from app.services.mail_sender_service import send_mail
        email_body = f"""
Kedves felhasználó!<br>
Erre az email címre egy bejelentkezési név emlékeztetőt kértek.<br>
<br>
Felhasználóneved: {user.username}<br>
<br>
Ha ezt az emlékeztetőt nem te kérted akkor lépj kapcsolatba az oldal üzemeltetőjével!<br>
Üdv,<br>
Groubite
"""
        ok, msg = send_mail([user.email], [], "Groupbite: Bejelentkezési adat emlékeztető", email_body)
        if not ok:
            return { "error": "Email szolgáltatás nem elérhető, küldés sikertelen" }, 200

    return { "msg": "Email reminder sent" }, 200

@user_blueprint.route("/register", methods=["POST"])
def handle_user_register():
    username = request.json["username"]
    email = request.json["email"]

    is_username_valid, username_error = User.is_username_valid(username)
    is_email_valid, email_error = User.is_email_valid(email)

    if not is_username_valid:
        return { "error": username_error }

    if not is_email_valid:
        return { "error": email_error }

    ok, user_to_register = User.create_user(User(username=username, email=email, settings={}, password=""))
    if ok:
        logging.info(f"User {user_to_register.username} created!")

        session["user_id"] = user_to_register.id
        session.permanent = True

        return { "data": user_to_register.serialized }, 201
    else:
        return { "error": "Failed to register, something wrong with the data you provided" }, 400


@user_blueprint.route("/<user_id>", methods=["PUT"])
@validate_url_params(IDSchema())
@require_auth
def handle_user_update(user_id):
    user = request.json["data"]

    user_to_update = User.get_one_by_id(user_id)

    if "username" in user:
        is_username_valid, error = User.is_username_valid(user["username"])
        if is_username_valid:
            user_to_update.update_user(user)
            logging.info("Updated User: " + str(user["id"]))
        else:
            logging.info("Invalid user update: " + error)
            return { "error": error }

    if "username" in user:
        logging.info("Updating username in rooms")
        # Updating the username in every basket(room) a user is in
        for room_name,room in socketio.server.manager.rooms["/"].items():
            if room_name != None and "@" in room_name:

                vendor, date = room_name.split("@")
                # TODO: check if user has items in that oreder, and only update them
                order = Order.find_order_by_date_for_a_vendor(vendor, date)
                socketio.emit(
                    "be_order_update", {
                        "basket": order.get_order_items()
                    },
                    to=room_name
                )

    return { "data": user_to_update.serialized }, 200


@user_blueprint.route("/<user_id>/orders", methods=["GET"])
@validate_url_params(IDSchema())
def handle_user_order_history(user_id):

    try:
        limit = int(request.args.get('limit'))
        page = int(request.args.get('page'))
    except ValueError as e:
        limit = 10
        page = 1
    except TypeError as e:
        limit = 10
        page = 1

    search = request.args.get('search')
    vendor_id = request.args.get('vendor_id')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    offset = 0 if page is None else limit * (page - 1)

    user_items = UserBasket.find_user_orders(user_id, limit, offset, search, vendor_id, date_from, date_to)
    all_items = UserBasket.find_user_orders(user_id, None, 0, search, vendor_id, date_from, date_to)

    vendors = UserBasket.find_user_order_vendors(user_id)

    vendors_list = [{
        "id": vendor.id,
        "title": vendor.name
    } for vendor in vendors]

    orders_dict = {}

    for item in user_items:
        order_id = item.order_id
        if order_id not in orders_dict:
            # Get all participants for this order to calculate user's share of fee
            order_participants_count = UserBasket.user_count(order_id)
            user_order_fee = item.order.order_fee / order_participants_count if order_participants_count > 0 else 0

            # Initialize order structure
            orders_dict[order_id] = {
                "id": item.order.id,
                "vendor": {
                    "name": item.order.vendor.name
                },
                "state_id": str(item.order.state_id),
                "date_of_order": item.order.date_of_order.strftime("%Y-%m-%d"),
                "order_time": item.order.order_time.isoformat() if item.order.order_time else None,
                "order_fee": user_order_fee,
                "total_price": 0,  # Will be calculated
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

    for order_data in orders_dict.values():
        order_data["total_price"] += order_data["order_fee"]

    # Convert to list and sort by date (most recent first)
    orders_list = list(orders_dict.values())
    orders_list.sort(key=lambda x: x["date_of_order"], reverse=True)

    unique_orders = set(item.order.id for item in all_items)
    total_orders = len(unique_orders)

    # Calculate total spending across all orders
    total_user_spending = 0
    processed_orders = set()

    for item in all_items:
        # Add item cost
        total_user_spending += item.total_price

        # Add user's share of order fee (only once per order)
        if item.order.id not in processed_orders:
            order_participants_count = UserBasket.user_count(item.order.id)
            user_order_fee = item.order.order_fee / order_participants_count if order_participants_count > 0 else 0
            total_user_spending += user_order_fee
            processed_orders.add(item.order.id)

    return { "data": {
        "items": orders_list,
        "vendors": vendors_list,
        "page": page,
        "limit": limit,
        "total_count": total_orders,
        "total_sum": total_user_spending
        }
    }, 200


@user_blueprint.route("/", methods=["GET"])
@require_auth
@require_admin
def handle_get_users():
    try:
        limit = int(request.args.get('limit'))
        page = int(request.args.get('page'))
    except ValueError as e:
        limit = 10
        page = 1
    except TypeError as e:
        limit = 10
        page = 1
    offset = 0 if page is None else limit * (page - 1)
    users = User.find_all(limit, offset)
    total_count = len(User.find_all())
    result = []
    for user in users:
        result.append(user.serialized)
    return { "data": {
                "items": result,
                "page": page,
                "limit": limit,
                "total_count": total_count
            }
        }, 200


@user_blueprint.route('/<user_id>/statistics', methods=["GET"])
@require_auth
def user_statistics(user_id):
    try:
        # Get all user's basket items
        all_user_items = UserBasket.find_user_orders(user_id)

        if not all_user_items:
            return {
                "statistics": {
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
            }, 200

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
            "statistics": {
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
        }, 200

    except Exception as e:
        print(f"Error calculating user statistics: {str(e)}")
        return {"error": "Failed to calculate statistics"}, 500

@user_blueprint.route('/<user_id>/spending-trends', methods=["GET"])
@require_auth
def user_spending_trends(user_id):
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

        return {
            "trends": trends
        }, 200

    except Exception as e:
        print(f"Error calculating spending trends: {str(e)}")
        return {"error": "Failed to calculate trends"}, 500

@user_blueprint.route('/<user_id>/vendor-breakdown', methods=["GET"])
@require_auth
def user_vendor_breakdown(user_id):
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

        return {
            "breakdown": breakdown
        }, 200

    except Exception as e:
        print(f"Error calculating vendor breakdown: {str(e)}")
        return {"error": "Failed to calculate breakdown"}, 500
