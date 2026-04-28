from sqlalchemy import Column,Integer,String,Boolean,Float,ForeignKey,Enum
from sqlalchemy.orm import relationship
from database import Base
import enum

class OrderStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    shipped = "shipped"
    cancelled = "cancelled"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True,index=True)
    email = Column(String,unique=True,index=True)
    hashed_password = Column(String,nullable=False)
    is_admin = Column(Boolean,default=False)
    orders = relationship("Order",back_populates="owner")
    cart_items = relationship("Cart",back_populates="owner")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer,primary_key=True,index=True)
    name = Column(String,index=True)
    price = Column(Float)
    stock = Column(Integer)
    cart_items = relationship("Cart",back_populates="product")

class Cart(Base):                                                   
    __tablename__ = "cart"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    owner = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(Integer,ForeignKey("users.id"))
    total_price = Column(Float)
    status = Column(Enum(OrderStatus),default=OrderStatus.pending)
    owner = relationship("User",back_populates="orders")
    items = relationship("OrderItem",back_populates="order")

class OrderItem(Base):                                          
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    price_at_purchase = Column(Float)
    order = relationship("Order", back_populates="items")

