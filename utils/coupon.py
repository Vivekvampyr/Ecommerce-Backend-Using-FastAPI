from fastapi import HTTPException
from models import Coupon, DiscountType
from datetime import datetime, timezone

def check_coupon(coupon: Coupon):
    """Validates a coupon exists and is usable — raises HTTPException if not"""
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    if not coupon.is_active:
        raise HTTPException(status_code=400, detail="Coupon is inactive")
    if coupon.expires_at and coupon.expires_at < datetime.now():
        raise HTTPException(status_code=400, detail="Coupon has expired")
    if coupon.max_uses is not None and coupon.used_count >= coupon.max_uses:
        raise HTTPException(status_code=400, detail="Coupon usage limit reached")

def apply_discount(total: float, coupon: Coupon) -> tuple[float, float]:
    """
    Returns (discounted_total, discount_amount)
    Ensures total never goes below 0
    """
    if coupon.discount_type == DiscountType.percentage:
        discount_amount = round(total * coupon.discount_value / 100, 2)
    else:
        discount_amount = round(min(coupon.discount_value, total), 2)  # can't exceed total

    discounted_total = round(total - discount_amount, 2)
    return discounted_total, discount_amount