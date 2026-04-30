from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from models import OrderStatus, DiscountType, PaymentStatus
from datetime import datetime

# ─── Payment ────────────────────────────────────────────────

class PaymentInitResponse(BaseModel):
    razorpay_order_id: str
    amount: float                   # in paise (INR × 100)
    currency: str
    order_id: int                   # our internal order id
    key_id: str                     # frontend needs this to open Razorpay popup

class PaymentVerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class PaymentResponse(BaseModel):
    id: int
    order_id: int
    razorpay_order_id: str
    razorpay_payment_id: Optional[str]
    amount: float
    currency: str
    status: PaymentStatus
    class Config:
        from_attributes = True

# ─── User ───────────────────────────────────────────────────

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_admin: bool
    avatar: Optional[str] = None
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# ─── Category ───────────────────────────────────────────────

class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    description: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    class Config:
        from_attributes = True

# ─── Review ─────────────────────────────────────────────────

class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)             # strictly 1-5 stars
    title: Optional[str] = Field(default=None, max_length=100)
    body: Optional[str] = Field(default=None, max_length=2000)

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    title: Optional[str] = Field(default=None, max_length=100)
    body: Optional[str] = Field(default=None, max_length=2000)

class ReviewAuthor(BaseModel):                  # nested in ReviewResponse
    id: int
    email: str
    avatar: Optional[str] = None
    class Config:
        from_attributes = True

class ReviewResponse(BaseModel):
    id: int
    product_id: int
    user_id: int
    rating: int
    title: Optional[str]
    body: Optional[str]
    created_at: datetime
    updated_at: datetime
    author: ReviewAuthor                        # shows who wrote it
    class Config:
        from_attributes = True

class ProductRatingSummary(BaseModel):          # aggregated stats for a product
    product_id: int
    average_rating: float
    total_reviews: int
    five_star: int
    four_star: int
    three_star: int
    two_star: int
    one_star: int

# ─── Product ────────────────────────────────────────────────

class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    category_id: Optional[int] = None

class ProductUpdate(BaseModel):                        # ← new — for editing products
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    category_id: Optional[int] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int
    category_id: Optional[int]
    category: Optional[CategoryResponse] = None
    average_rating: Optional[float] = None    
    total_reviews: Optional[int] = None 
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
    product: ProductResponse
    class Config:
        from_attributes = True

# ─── Coupon ─────────────────────────────────────────────────

class CouponCreate(BaseModel):
    code: str = Field(min_length=3, max_length=20)
    discount_type: DiscountType
    discount_value: float = Field(gt=0)
    min_order_amount: float = Field(default=0.0, ge=0)
    max_uses: Optional[int] = None                      # None = unlimited
    expires_at: Optional[datetime] = None               # None = never expires

class CouponResponse(BaseModel):
    id: int
    code: str
    discount_type: DiscountType
    discount_value: float
    min_order_amount: float
    max_uses: Optional[int]
    used_count: int
    is_active: bool
    expires_at: Optional[datetime]
    class Config:
        from_attributes = True

class ApplyCoupon(BaseModel):
    code: str                                           # user sends this at checkout

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
    discount_amount: float                              # ← new
    coupon_code: Optional[str]                         # ← new
    status: OrderStatus
    items: List[OrderItemResponse]
    payment: Optional[PaymentResponse] = None
    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: OrderStatus