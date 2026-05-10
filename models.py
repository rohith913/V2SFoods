from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class AdminMaster(Base):
    __tablename__ = "admin_master"

    id = Column(Integer, primary_key=True, index=True)
    admin_name = Column(String(200))
    mobile = Column(String(20))
    email = Column(String(300), unique=True, nullable=False)
    password = Column(String(300), nullable=False)
    role = Column(String(50), default="ADMIN")
    status = Column(String(50), default="ACTIVE")
    created_datetime = Column(DateTime, default=datetime.utcnow)


class UserMaster(Base):
    __tablename__ = "user_master"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(200))
    mobile = Column(String(20))
    email = Column(String(300), unique=True)
    password = Column(String(300))
    status = Column(String(50), default="ACTIVE")
    created_datetime = Column(DateTime, default=datetime.utcnow)

    orders = relationship("OrderMaster", back_populates="user")


class ItemMaster(Base):
    __tablename__ = "item_master"

    id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String(100), unique=True)
    item_name = Column(String(300))
    description = Column(Text)
    category = Column(String(200))
    price = Column(Numeric(10, 2))
    stock_qty = Column(Integer, default=0)
    image_url = Column(Text)
    status = Column(String(50), default="ACTIVE")
    created_datetime = Column(DateTime, default=datetime.utcnow)


class CartMaster(Base):
    __tablename__ = "cart_master"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_master.id"))
    item_id = Column(Integer, ForeignKey("item_master.id"))
    qty = Column(Integer, default=1)
    created_datetime = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserMaster")
    item = relationship("ItemMaster")


class OrderMaster(Base):
    __tablename__ = "order_master"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(100), unique=True)
    user_id = Column(Integer, ForeignKey("user_master.id"))
    total_amount = Column(Numeric(10, 2))
    status = Column(String(50), default="BOOKED")
    booking_datetime = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserMaster", back_populates="orders")
    details = relationship("OrderDetail", back_populates="order")


class OrderDetail(Base):
    __tablename__ = "order_detail"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order_master.id"))
    item_id = Column(Integer, ForeignKey("item_master.id"))
    qty = Column(Integer)
    price = Column(Numeric(10, 2))
    amount = Column(Numeric(10, 2))

    order = relationship("OrderMaster", back_populates="details")
    item = relationship("ItemMaster")