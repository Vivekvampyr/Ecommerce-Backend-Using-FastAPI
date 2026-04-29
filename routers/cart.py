from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List,Optional
from database import get_db
from auth import get_current_user
from schemas import CartAdd, CartItemResponse, OrderResponse,ApplyCoupon
import models
from utils.coupon import check_coupon,apply_discount

router = APIRouter(prefix='/cart',tags=['Cart'])

@router.get("/",response_model=List[CartItemResponse])
def view_cart(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(models.Cart).filter(models.Cart.user_id == current_user.id).all()

@router.post("/add")
def add_to_cart(data: CartAdd,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    product = db.query(models.Product).filter(models.Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404,detail="Product not Found")
    if product.stock < data.quantity:
        raise HTTPException(status_code=400,detail="Insufficient stock")
    
    # If already in cart, Just increase quantity
    existing = db.query(models.Cart).filter(models.Cart.user_id == current_user.id,models.Cart.product_id == data.product_id).first()
    if existing:
        existing.quantity += data.quantity
    else:
        db.add(models.Cart(user_id=current_user.id,product_id=data.product_id,quantity=data.quantity))
    
    db.commit()
    return {"msg":"Added to cart"}

@router.patch("/update/{item_id}")
def update_cart_item(item_id: int, quantity: int, db:Session=Depends(get_db), current_user=Depends(get_current_user)):
    item = db.query(models.Cart).filter(models.Cart.id == item_id,models.Cart.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404,detail="Cart item not Found")
    if quantity <= 0:
        db.delete(item)
    else:
        item.quantity = quantity
    db.commit()
    return {"msg":"Cart updated successfully"}

@router.delete("/remove/{item_id}")
def remove_from_cart(item_id: int, db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    item = db.query(models.Cart).filter(models.Cart.id==item_id,models.Cart.user_id==current_user.id).first()
    if not item:
        raise HTTPException(status_code=404,detail="Cart item not found")
    db.delete(item)
    db.commit()
    return {"msg":"Item Removed"}

@router.post("/checkout",response_model=OrderResponse)
def checkout(coupon_data: Optional[ApplyCoupon] = None, db:Session=Depends(get_db), current_user=Depends(get_current_user)):
    cart_items = db.query(models.Cart).filter(models.Cart.user_id==current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400,detail="Cart is Emply")
    
    #Validate all items first before changing anything
    for item in cart_items:
        if not item.product or item.product.stock < item.quantity:
            raise HTTPException(status_code=400,detail=f"Insufficient stock for {item.product.name if item.product else item.product_id}")
        
    # Calculate Total
    total = round(sum(item.product.price * item.quantity for item in cart_items), 2)

    # Apply coupon if provided
    discount_amount = 0.0
    coupon_code = None
    coupon = None

    if coupon_data:
        coupon = db.query(models.Coupon).filter(models.Coupon.code == coupon_data.code.upper()).first()
        check_coupon(coupon)

        if total < coupon.min_order_amount:
            raise HTTPException(status_code=400,detail=f"Minimum order amount for this coupon is rs.{coupon.min_order_amount}")
    
        final_total, discount_amount = apply_discount(total,coupon)
        coupon_code = coupon.code
    else:
        final_total = total

    order = models.Order(user_id=current_user.id,total_price=final_total,discount_amount=discount_amount,coupon_code=coupon_code)
    db.add(order)
    db.flush()

    # Create order items, deduct stock, clear cart
    for item in cart_items:
        db.add(models.OrderItem(order_id=order.id,product_id=item.product.id,quantity=item.quantity,price_at_purchase=item.product.price))
        item.product.stock -= item.quantity
        db.delete(item)
    
    # Increment coupon usage
    if coupon:
        coupon.used_count += 1
    
    db.commit()
    db.refresh(order)
    return order
    
