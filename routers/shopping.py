from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from auth import get_current_user,require_admin
from database import get_db
import models

router = APIRouter(prefix="/shopping", tags=["Shopping"])

@router.get("/products")
def list_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

@router.post("/product")
def add_product(name: str, price: float, stock: int, db: Session = Depends(get_db), admin = Depends(require_admin)):
    product = models.Product(name=name,price=price,stock=stock)
    db.add(product)
    db.commit()
    return {"msg":"Product added"}

@router.post("/orders")
def place_order(product_id: int, quantity: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product or product.stock < quantity:
        raise HTTPException(status_code=400,detail="Product Unavailable")
    product.stock -= quantity
    order = models.Order(user_id=current_user.id,product_id=product_id,quantity=quantity)
    db.add(order)
    db.commit()
    return {"msg": "Order Places"}

@router.get("/orders/me")
def my_orders(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(models.Order).filter(models.Order.user_id == current_user.id).all()
