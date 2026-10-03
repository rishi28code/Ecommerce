from sqlalchemy import Column, Enum, Integer, String, Float, TIMESTAMP, ForeignKey
from sqlalchemy.orm import (
    declarative_base,
    relationship
)
from datetime import datetime
import enum
from sqlalchemy import Enum


Base = declarative_base()


# 🔐 Role Enum
class RoleEnum(str, enum.Enum):
    user = "user"
    admin = "admin"
    customer = "customer"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String,unique=True,index=True,nullable=False)

    password = Column(String, nullable=False)

    role = Column(Enum(RoleEnum),default=RoleEnum.user)

    # one user -> many orders
    orders = relationship("Order",back_populates="user")


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)

    description = Column(String)

    price = Column(Float)

    quantity = Column(Integer)

    # one product -> many order items
    order_items = relationship("OrderItem",back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer,ForeignKey("users.id"))

    description = Column(String)

    created_at = Column(TIMESTAMP,default=datetime.utcnow)

    # many orders -> one user
    user = relationship("User",back_populates="orders")

    # one order -> many order items
    items = relationship("OrderItem",back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer,ForeignKey("orders.id"))

    product_id = Column(Integer,ForeignKey("product.id"))

    quantity = Column(Integer)

    # many order items -> one order
    order = relationship("Order",back_populates="items")

    # many order items -> one product
    product = relationship("Product",back_populates="order_items")
   