from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from auth import get_current_user, require_admin
from schemas import CouponCreate, CouponResponse
from models import Coupon
from datetime import datetime, timezone
from utils.coupon import check_coupon,apply_discount

router = APIRouter(prefix="/coupons", tags=["Coupons"])

@router.post("/",response_model=CouponResponse)
def create_coupon(data:CouponCreate,db:Session=Depends(get_db),admin=Depends(require_admin)):
    if db.query(Coupon).filter(Coupon.code == data.code.upper()).first():
        raise HTTPException(status_code=400,detail="Coupon already exists")
    coupon = Coupon(
        code=data.code.upper(),
        discount_type=data.discount_type,
        discount_value=data.discount_value,
        min_order_amount=data.min_order_amount,
        max_uses=data.max_uses,
        expires_at=data.expires_at,
    )
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return coupon

@router.get("/",response_model=List[CouponResponse])
def list_coupons(db:Session=Depends(get_db), admin=Depends(require_admin)):
    return db.query(Coupon).all()

@router.patch("/{coupon_id}/toggle")
def toggle_coupon(coupon_id: int, db:Session=Depends(get_db),admin=Depends(require_admin)):
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(status_code=404,detail="Coupon not found")
    coupon.is_active = not coupon.is_active
    db.commit()
    db.refresh(coupon)
    return coupon

@router.delete("/{coupon_id}")
def delete_coupon(coupon_id: int, db:Session=Depends(get_db),admin=Depends(require_admin)):
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(status_code=404,detail="Coupon not found")
    db.delete(coupon)
    db.commit()
    return {"msg":"Coupon Deleted"}

@router.get("/validate/{code}")
def validate_coupon(code: str,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    coupon = db.query(Coupon).filter(Coupon.code == code.upper()).first()
    check_coupon(coupon)
    return {
        "code":coupon.code,
        "discount_type":coupon.discount_type,
        "discount_value":coupon.discount_value,
        "min_order_amount":coupon.min_order_amount,
    }