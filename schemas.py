from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8,max_digits=72)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_admin: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ProductCreate(BaseModel):
    name: str = Field(min_length=1,max_length=100)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock: int

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    product_id: int
    quantity: int = Field(ge=1)

class OrderResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True