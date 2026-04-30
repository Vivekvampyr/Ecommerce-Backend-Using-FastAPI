from sqlalchemy import Column,Integer,String,Boolean,Float,ForeignKey,Enum, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class OrderStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    shipped = "shipped"
    cancelled = "cancelled"


class DiscountType(str, enum.Enum):     # ← new
    percentage = "percentage"           # e.g. 20% off
    fixed      = "fixed"                # e.g. ₹100 off

class PaymentStatus(str, enum.Enum):   
    created  = "created"
    paid     = "paid"
    failed   = "failed"
    refunded = "refunded"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True,index=True)
    email = Column(String,unique=True,index=True)
    hashed_password = Column(String,nullable=True) # for OAuth users, this can be null
    is_admin = Column(Boolean,default=False)
    google_id = Column(String,unique=True,nullable=True) # for Google OAuth users
    avatar = Column(String,nullable=True) # URL to profile picture
    orders = relationship("Order",back_populates="owner")
    cart_items = relationship("Cart",back_populates="owner")
    reviews = relationship("Review",back_populates="author")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String,unique=True,index=True)
    description = Column(String,nullable=True)
    products = relationship("Product",back_populates="category")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer,primary_key=True,index=True)
    name = Column(String,index=True)
    description = Column(String,nullable=True)
    price = Column(Float)
    stock = Column(Integer)
    category_id = Column(Integer,ForeignKey("categories.id"),nullable=True)
    category = relationship("Category",back_populates="products")
    cart_items = relationship("Cart",back_populates="product")
    reviews = relationship("Review",back_populates="product")

class Cart(Base):                                                   
    __tablename__ = "cart"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    owner = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

class Coupon(Base):                                         # ← new
    __tablename__ = "coupons"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)          # e.g. "SAVE20"
    discount_type = Column(Enum(DiscountType))              # percentage or fixed
    discount_value = Column(Float)                          # 20.0 or 100.0
    min_order_amount = Column(Float, default=0.0)           # minimum cart total to apply
    max_uses = Column(Integer, default=None)                # None = unlimited
    used_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)            # None = never expires


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(Integer,ForeignKey("users.id"))
    total_price = Column(Float)
    discount_amount = Column(Float, default=0.0)
    coupon_code = Column(String, nullable=True)
    status = Column(Enum(OrderStatus),default=OrderStatus.pending)
    owner = relationship("User",back_populates="orders")
    items = relationship("OrderItem",back_populates="order")
    payment = relationship("Payment", back_populates="order",uselist=False)

class OrderItem(Base):                                          
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    price_at_purchase = Column(Float)
    order = relationship("Order", back_populates="items")

class Payment(Base):                                       
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True)
    razorpay_order_id = Column(String, unique=True)         # from Razorpay
    razorpay_payment_id = Column(String, nullable=True)     # filled after payment
    razorpay_signature = Column(String, nullable=True)      # for verification
    amount = Column(Float)                                  # in INR
    currency = Column(String, default="INR")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.created)
    order = relationship("Order", back_populates="payment")

class Review(Base):                                                 # ← new
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Integer)                                        # 1 to 5
    title = Column(String, nullable=True)                           # short headline
    body = Column(Text, nullable=True)                              # full review text
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    product = relationship("Product", back_populates="reviews")
    author = relationship("User", back_populates="reviews")
