from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from auth import get_current_user, require_admin
from schemas import OrderResponse, OrderStatusUpdate
from models import Order, OrderStatus,Product

router = APIRouter(prefix="/orders", tags=["Orders"])

# ─── Valid transitions ───────────────────────────────────────
# Defines what status can move to what next
ALLOWED_TRANSITIONS = {
    OrderStatus.pending:   [OrderStatus.paid,     OrderStatus.cancelled],
    OrderStatus.paid:      [OrderStatus.shipped,  OrderStatus.cancelled],
    OrderStatus.shipped:   [],       # final state — cannot change
    OrderStatus.cancelled: [],       # final state — cannot change
}

@router.get("/me",response_model=List[OrderResponse])
def my_orders(db:Session=Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Order).filter(Order.user_id == current_user.id).all()

@router.get("/me/{order_id}", response_model=OrderResponse)
def get_my_order(order_id: int, db:Session=Depends(get_db), current_user=Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id,Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404,detail="Order not Found")
    return order

@router.patch("/me/{order_id}/cancel",response_model=OrderResponse)
def cancel_my_order(order_id: int, db:Session=Depends(get_db), current_user=Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404,detail="Order not Found")
    if order.status != OrderStatus.pending:
        raise HTTPException(status_code=400,detail=f"Only pending order can be cancelled. Order status: {order.status}")
    # restore stock when cancelled
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.stock += item.quantity
        
    order.status = OrderStatus.cancelled
    db.commit()
    db.refresh(order)
    return order

# Admin Routes
@router.get("/all",response_model=List[OrderResponse])
def all_orders(status: OrderStatus = None,db:Session=Depends(get_db),admin=Depends(require_admin)):
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    return query.all()

@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(order_id: int, data: OrderStatusUpdate, db: Session=Depends(get_db), admin=Depends(require_admin)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404,detail="Order not found")
    allowed = ALLOWED_TRANSITIONS.get(order.status,[])
    if data.status not in allowed:
        raise HTTPException(status_code=400,detail=f"Cannot move from {order.status} to {data.status}. Allowed: {[s.value for s in allowed] or 'none (final state)'}")
    
    order.status = data.status
    db.commit()
    db.refresh(order)
    return order
