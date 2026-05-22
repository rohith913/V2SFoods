from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text, Boolean, JSON
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
    ingredients = Column(Text)
    how_to_use = Column(Text)
    specifications = Column(Text)
    price = Column(Numeric(10, 2))
    stock_qty = Column(Integer, default=0)
    main_image = Column(Text)
    image_1 = Column(Text)
    image_2 = Column(Text)
    image_3 = Column(Text)
    image_4 = Column(Text)
    image_5 = Column(Text)
    video_url = Column(Text)
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
    selected_kg = Column(Numeric(5, 2), default=0.5)


class OrderMaster(Base):
    __tablename__ = "order_master"
    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(100), unique=True)
    invoice_no = Column(String(100), unique=True, nullable=True)
    user_id = Column(Integer, ForeignKey("user_master.id"))
    total_amount = Column(Numeric(10, 2))
    status = Column(String(50), default="BOOKED")
    booking_datetime = Column(DateTime, default=datetime.utcnow)

    # Delivery details
    cust_name = Column(String(200))
    cust_mobile = Column(String(20))
    cust_address = Column(Text)
    cust_city = Column(String(100))
    cust_state = Column(String(100))
    cust_pincode = Column(String(10))
    payment_method = Column(String(50), default="COD")

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
    selected_kg = Column(Numeric(5, 2), default=0.5)


class RecipeLike(Base):
    __tablename__ = "recipe_like"
    id = Column(Integer, primary_key=True, index=True)
    recipe_slug = Column(String(100), index=True)
    user_email = Column(String(300))
    created_datetime = Column(DateTime, default=datetime.utcnow)


class RecipeComment(Base):
    __tablename__ = "recipe_comment"
    id = Column(Integer, primary_key=True, index=True)
    recipe_slug = Column(String(100), index=True)
    author_name = Column(String(200))
    author_email = Column(String(300))
    comment = Column(Text)
    approved = Column(Boolean, default=True)
    created_datetime = Column(DateTime, default=datetime.utcnow)


# ── Dynamic Recipe Model ─────────────────────────────────────────────────────
class RecipeMaster(Base):
    __tablename__ = "recipe_master"
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(200), unique=True, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    category = Column(String(200))
    time_minutes = Column(String(50))   # e.g. "20 minutes"
    servings = Column(String(100))      # e.g. "2 servings"
    difficulty = Column(String(50))     # Easy / Medium / Hard
    emoji = Column(String(20), default="🍲")
    about = Column(Text)
    # JSON arrays stored as Text
    ingredients_json = Column(Text, default="[]")
    steps_json = Column(Text, default="[]")
    tips_json = Column(Text, default="[]")
    nutrition_json = Column(Text, default="{}")
    image_url = Column(Text, default="")
    status = Column(String(20), default="ACTIVE")
    created_datetime = Column(DateTime, default=datetime.utcnow)
