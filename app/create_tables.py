from app.entities import Base, engine
from app.entities.user import User, Theme
from app.entities.menu import Menu, Frequency
from app.entities.order import Order, OrderState
from app.entities.vendor import Vendor, VendorType
from app.entities.menu_item import MenuItem
from app.entities.user_basket import UserBasket
import logging


logging.info("Creating Database tables:")
Base.metadata.create_all(bind=engine)
