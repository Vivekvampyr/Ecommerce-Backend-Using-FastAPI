from pydantic import BaseModel, EmailStr, Field
from typing import List
from models import OrderStatus

# ─── User ───────────────────────────────────────────────────

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_admin: bool
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# ─── Product ────────────────────────────────────────────────

class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock: int
    class Config:
        from_attributes = True

# ─── Cart ───────────────────────────────────────────────────

class CartAdd(BaseModel):
    product_id: int
    quantity: int = Field(ge=1)

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: ProductResponse           # nested — shows full product details
    class Config:
        from_attributes = True

# ─── Order ──────────────────────────────────────────────────

class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    price_at_purchase: float
    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_price: float
    status: OrderStatus
    items: List[OrderItemResponse]
    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: OrderStatus