import enum, json
from typing import List
from . import Base, session
from .vendor import Vendor
from uuid import UUID
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from sqlalchemy import ForeignKey, select, exc, extract
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from marshmallow import Schema, fields
import logging

class BaseOrderSchema(Schema):
    state_id = fields.Str(required=True)
    order_fee = fields.Int(required=True)

class OrderState(enum.Enum):
    COLLECT = "collect"
    ORDER = "order"
    CLOSED = "closed"

    def __str__(self):
        return self.value


class Order(Base):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    vendor_id: Mapped[UUID] = mapped_column(ForeignKey("vendor.id"))
    state_id: Mapped[OrderState] = mapped_column(default=OrderState.COLLECT)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"),nullable=True)
    date_of_order: Mapped[date]
    order_time: Mapped[datetime] = mapped_column(nullable=True)
    order_fee: Mapped[int] = mapped_column(default=0)
    total_price: Mapped[int] = mapped_column(default=0)

    items: Mapped[List["UserBasket"]] = relationship(back_populates="order")
    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="order")
    vendor: Mapped["Vendor"] = relationship(back_populates="orders")
    ordered_by: Mapped["User"] = relationship(back_populates="placed_orders")

    def __repr__(self):
        return f"Order<id={self.id},order_time={self.order_time},vendor_id={self.vendor_id},state_id={str(self.state_id)},user_id={self.user_id},date_of_order={self.date_of_order},order_time={self.order_time}>"

    def create_order(v_id: UUID, doo: date = date.today()):
        vendor = Vendor.find_by_id(v_id)
        order = Order(vendor_id=v_id, date_of_order=doo, order_fee=vendor.settings["transport_price"]["value"])
        session.add(order)
        try:
            session.commit()
            session.refresh(order)
            return True, order
        except exc.DataError as e:
            logging.exception("DataError during order add")
            session.rollback()
            return False, None
        except Exception as e:
            logging.exception("Unhadled exception happened, rolling back")
            session.rollback()
            return False, None

    def get_by_id(order_id):
        stmt = select(Order).where(Order.id == order_id)
        return session.execute(stmt).scalars().first()


    def last_7_days_statistics():
        result = {}
        last_7_days = [(date.today() - relativedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
        last_7_days.reverse()
        for vendor in Vendor.find_all_active():
            result[vendor.name] = {
            "data": []
            }
            for day in last_7_days:
                parsed_date = datetime.strptime(day, "%Y-%m-%d")
                result[vendor.name]["data"].append(Order.day_sum_by_vendor(vendor.id, parsed_date.year, parsed_date.month, parsed_date.day))

        return result, last_7_days


    def last_12_month_statistics():
        result = {}
        last_12_months = [(date.today() - relativedelta(months=i)).strftime("%Y-%m") for i in range(12)]
        last_12_months.reverse()
        for vendor in Vendor.find_all_active():
            result[vendor.name] = {
                "data": []
            }
            for month in last_12_months:
                parsed_date = datetime.strptime(month, "%Y-%m")
                result[vendor.name]["data"].append(Order.month_sum_by_vendor(vendor.id, parsed_date.year, parsed_date.month))


        return result, last_12_months


    def month_sum_by_vendor(vendor_id, year, month):
        stmt = select(Order).where(
            Order.vendor_id == vendor_id,
            extract("year", Order.date_of_order) == year,
            extract("month", Order.date_of_order) == month
        )

        orders = session.execute(stmt).scalars()
        sum = 0
        for order in orders:
            for basket_entry in order.order_items:
                sum += basket_entry.total_price
            if len(order.get_order_items()) != 0:
                sum += order.order_fee


        return sum

    def day_sum_by_vendor(vendor_id, year, month, day):
        stmt = select(Order).where(
            Order.vendor_id == vendor_id,
            extract("year", Order.date_of_order) == year,
            extract("month", Order.date_of_order) == month,
            extract("day", Order.date_of_order) == day
        )

        orders = session.execute(stmt).scalars()
        sum = 0
        for order in orders:
            for basket_entry in order.order_items:
                sum += basket_entry.total_price
            if len(order.get_order_items()) != 0:
                sum += order.order_fee


        return sum

    def find_orders_between_dates(start, end):
        stmt = select(
            Order.id,
            Order.date_of_order,
            Order.state_id
        ).join(
            Order.order_items
        ).where(
            Order.date_of_order.between(start, end)
        )
        return session.execute(stmt).all()


    def find_user_order_dates_between(user_id, start, end):
        from .order_item import OrderItem
        stmt = select(
            Order
        ).join(
            Order.order_items
        ).where(
            OrderItem.user_id == user_id,
            Order.date_of_order.between(start, end)
        )
        return session.execute(stmt).scalars().all()

    def find_all(limit=None, offset=0):
        stmt = select(Order).order_by(Order.date_of_order.desc())
        if limit is not None:
            stmt = stmt.limit(limit).offset(offset)
        return session.execute(stmt).scalars().all()

    def find_open_order_by_date_for_a_vendor(vendor_id: UUID, date: date = date.today()):
        stmt = select(Order).where(
            Order.vendor_id == vendor_id,
            Order.date_of_order == date,
            Order.state_id != OrderState.CLOSED)
        return session.execute(stmt).scalars().first()

    def find_order_by_date_for_a_vendor(vendor_id: UUID, date: date = date.today()):
        stmt = select(Order).where(
            Order.vendor_id == vendor_id,
            Order.date_of_order == date)
        return session.execute(stmt).scalars().first()

    def find_order_between(date_from, date_to):
        stmt = select(Order).where(
            Order.date_of_order.between(date_from, date_to)
        )
        return session.execute(stmt).all()

    def find_order_participants(order_id):
        from .user import User
        from .user_basket import UserBasket
        stmt = select(User).distinct().join(
                UserBasket, User.id == UserBasket.user_id
            ).where(
                UserBasket.order_id == order_id
            )
        return session.execute(stmt).all()

    def get_order_items(self, user_filter=None):
        """
        Get order items grouped by user (uses order_items if closed, otherwise basket items)

        Args:
            user_filter: Optional filter - can be:
                - UUID/str: Return only items for this specific user
                - List[UUID/str]: Return items for these users only
                - None: Return items for all users


        Returns:
            dict: Items grouped by user_id with format:
            {
                "user_id_1": {
                    "user_id": "user_id_1",
                    "items": [...]
                },
                ...
            }
        """
        # Convert single user filter to list for uniform handling
        if user_filter is not None:
            if not isinstance(user_filter, (list, tuple, set)):
                user_filter = [user_filter]
            # Convert to strings for comparison
            user_filter = [str(uid) for uid in user_filter]

        result = {}

        if self.state_id == OrderState.CLOSED:
            # Use order_items for closed orders (snapshotted data)
            items_source = self.order_items
        else:
            # Use live basket data for non-closed orders
            items_source = self.items

        for item in items_source:
            user_id_str = str(item.user_id)

            # Apply user filter if specified
            if user_filter is not None and user_id_str not in user_filter:
                continue

            # Initialize user entry if not exists
            if user_id_str not in result:
                result[user_id_str] = {
                    "user_id": user_id_str,
                    "items": []
                }

                # Add username if requested and available
            result[user_id_str]["username"] = item.user.username if item.user else "Unknown"

            # Format item data
            if self.state_id == OrderState.CLOSED:
                # Use snapshotted data from order_items
                item_data = {
                    "item_id": item.menu_item_id,
                    "size_id": item.size_id,
                    "item_name": item.item_name,
                    "size_name": item.size_label,
                    "price": item.unit_price,
                    "category": None,  # Not stored in order_items, could be added if needed
                    "quantity": item.count,
                    "total_price": item.total_price
                }
            else:
                # Use live data from basket items
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


    def get_users(self):
        from .user import User
        from .user_basket import UserBasket
        stmt = select(User).distinct().join(
                UserBasket, User.id == UserBasket.user_id
            ).where(
                UserBasket.order_id == self.id
            )
        return session.execute(stmt).all()

    def change_state(self, new_state, user_id=None):
        """
        Change order state and handle order item creation/deletion

        Args:
            new_state: The new OrderState
            user_id: User ID if changing the order_by field

        Returns:
            bool: True if successful, False otherwise
        """
        from .order_item import OrderItem

        try:
            # If changing FROM CLOSED state to any other state, delete existing order items
            if self.state_id == OrderState.CLOSED and new_state != OrderState.CLOSED:
                self._delete_order_items()

            # Update state and user
            old_state = self.state_id
            self.state_id = new_state
            if user_id:
                self.order_by = user_id

            # If changing TO CLOSED state, create order items and calculate total
            if new_state == OrderState.CLOSED and old_state != OrderState.CLOSED:
                success = self._create_order_items_and_calculate_total()
                if not success:
                    # Rollback state change if order item creation failed
                    self.state_id = old_state
                    session.rollback()
                    return False

            session.commit()
            return True

        except exc.DataError as e:
            logging.exception("DataError during order state change")
            session.rollback()
            return False
        except Exception as e:
            logging.exception("Unhandled exception during order state change")
            session.rollback()
            return False

    def _delete_order_items(self):
        """Delete all order items for this order"""
        from .order_item import OrderItem
        session.query(OrderItem).filter(OrderItem.order_id == self.id).delete()

    def _create_order_items_and_calculate_total(self):
        """
        Create order items from user basket and calculate total price

        Returns:
            bool: True if successful, False otherwise
        """
        from .order_item import OrderItem

        order_price = 0
        created_items = []

        try:
            # Create order items from basket items
            for basket_item in self.items:
                # Create OrderItem with snapshotted data
                order_item = OrderItem(
                    order_id=self.id,
                    menu_item_id=basket_item.menu_item_id,
                    size_id=basket_item.size_id,
                    user_id=basket_item.user_id,
                    count=basket_item.count,
                    item_name=basket_item.item.name,
                    size_label=basket_item.size.name,
                    unit_price=basket_item.size.price,
                    total_price=basket_item.size.price * basket_item.count
                )

                session.add(order_item)
                created_items.append(order_item)
                order_price += order_item.total_price

            # Add order fee to total price
            order_price += self.order_fee
            self.total_price = order_price

            # Flush to get any database errors before final commit
            session.flush()
            return True

        except Exception as e:
            logging.exception("Error creating order items")
            # Clean up any partially created items
            for item in created_items:
                session.expunge(item)
            return False

    def set_order_fee(self, fee):
        self.order_fee = fee
        try:
            session.commit()
            return True
        except exc.DataError as e:
            logging.exception("DataError during order add")
            session.rollback()
            return False
        except Exception as e:
            logging.exception("Unhadled exception happened, rolling back")
            session.rollback()
            return False

    @property
    def serialized(self):
        return {
            "id": self.id,
            "vendor_id": str(self.vendor_id),
            "vendor": str(self.vendor.name),
            "state_id": str(self.state_id),
            "user_id": str(self.user_id),
            "date_of_order": self.date_of_order.strftime("%Y-%m-%d"),
            "order_time": self.order_time,
            "order_fee": self.order_fee,
            "total_price": self.total_price
        }
