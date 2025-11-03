from app.entities.order_item import OrderItem
from app.entities.order import Order
from app.entities.user import User
from app.entities.user_basket import UserBasket
from sqlalchemy import ForeignKey, select, exc, extract, Index, text, func, and_
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import date
from uuid import UUID
import logging
import re

class OrderItemRepository:

    def save(self, db, order_item: OrderItem):
        db.add(order_item)
