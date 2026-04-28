from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from auth import get_current_user,require_admin
from database import get_db
import models
from typing import List
from schemas import ProductCreate, ProductResponse

router = APIRouter(prefix="/shopping", tags=["Shopping"])

@router.get("/products", response_model=List[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

@router.post("/product",response_model=ProductResponse)
def add_product(data: ProductCreate, db: Session = Depends(get_db), admin = Depends(require_admin)):
    product = models.Product(name=data.name,price=data.price,stock=data.stock)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

# @router.post("/orders", response_model=ProductResponse)
# def place_order(data: ProductCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
#     product = db.query(models.Product).filter(models.Product.id == data.product_id).first()
#     if not product or product.stock < data.quantity:
#         raise HTTPException(status_code=400,detail="Product Unavailable")
#     product.stock -= data.quantity
#     order = models.Order(user_id=current_user.id,product_id=data.quantity,quantity=data.quantity)
#     db.add(order)
#     db.commit()
#     db.refresh(order)
#     return order

# @router.get("/orders/me", response_model=List[ProductResponse])
# def my_orders(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
#     return db.query(models.Order).filter(models.Order.user_id == current_user.id).all()
