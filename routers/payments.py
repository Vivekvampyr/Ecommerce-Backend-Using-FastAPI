import hmac
import hashlib
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user, require_admin
from schemas import PaymentInitResponse, PaymentVerifyRequest, PaymentResponse
from models import Order, Payment, OrderStatus, PaymentStatus
from utils.razorpay_client import client
from utils.limiter import limiter
from config import settings
from typing import List
import requests

router = APIRouter(prefix="/payments", tags=["Payments"])

# Create Razorpay Order
@router.post("/initiate/{order_id}",response_model=PaymentInitResponse)
def initiate_payment(request: Request, order_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != OrderStatus.pending:
        raise HTTPException(status_code=400, detail=f"Order is already {order.status}")

    existing = db.query(Payment).filter(Payment.order_id == order_id).first()
    if existing and existing.status == PaymentStatus.paid:
        raise HTTPException(status_code=400, detail="Order already paid")

    amount_in_paise = int(order.total_price * 100)

    # ✅ Wrapped in try/except — clean error instead of 500
    try:
        razorpay_order = client.order.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": f"order_{order.id}",
            "payment_capture": 1
        })
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Cannot reach Razorpay — check your internet connection or Razorpay credentials"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Razorpay error: {str(e)}")

    if existing:
        existing.razorpay_order_id = razorpay_order["id"]
        existing.status = PaymentStatus.created
    else:
        db.add(Payment(
            order_id=order.id,
            razorpay_order_id=razorpay_order["id"],
            amount=order.total_price,
            currency="INR",
        ))

    db.commit()

    return {
        "razorpay_order_id": razorpay_order["id"],
        "amount": amount_in_paise,
        "currency": "INR",
        "order_id": order.id,
        "key_id": settings.RAZORPAY_KEY_ID
    }

# Verify payment after user pays
@router.post("/verify/{order_id}", response_model=PaymentResponse)
def verify_payment(request: Request, order_id: int, data: PaymentVerifyRequest, db:Session=Depends(get_db), current_user=Depends(get_current_user)):
    payment = db.query(Payment).filter(Payment.order_id == order_id).first()
    if not payment:
        raise HTTPException(status_code=404,detail="Payment record not found")
    
    # ─── Signature verification ─────────────────────────────
    # Razorpay signs: razorpay_order_id + "|" + razorpay_payment_id
    body = f"{data.razorpay_order_id}|{data.razorpay_payment_id}"
    expected_signature = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()

    if expected_signature != data.razorpay_signature:
        payment.status = PaymentStatus.failed
        db.commit()
        raise HTTPException(status_code=400,detail="Payment verification failed - invalid signature")
    
    # Signature valid mark as paid
    payment.razorpay_payment_id = data.razorpay_payment_id
    payment.razorpay_signature = data.razorpay_signature
    payment.status = PaymentStatus.paid

    # Advance order status to paid
    order = db.query(Order).filter(Order.id == order_id).first()
    order.status = OrderStatus.paid
    db.commit()
    db.refresh(payment)
    return payment

# Admin: View all payments
@router.get("/all",response_model=List[PaymentResponse])
def all_payments(status: PaymentStatus = None,db:Session=Depends(get_db),admin=Depends(require_admin)):
    query = db.query(Payment)
    if status:
        query = query.filter(Payment.status == status)
    return query.all()

# Admin: refund a payment
@router.post("/refund{order_id}",response_model=PaymentResponse)
def refund_payment(order_id: int,db:Session=Depends(get_db),admin=Depends(require_admin)):
    payment = db.query(Payment).filter(Payment.order_id == order_id).first()
    if not payment:
        raise HTTPException(status_code=404,detail="Payment not found")
    if payment.status != PaymentStatus.paid:
        raise HTTPException(status_code=400,detail="Only paid order can be refunded")

    # Issue refund via Razorpay
    client.payment.refund(payment.razorpay_payment_id, {
        "amount": int(payment.amount * 100),    # full refund in paise
        "speed": "normal",
    })

    payment.status = PaymentStatus.refunded
    order = db.query(Order).filter(Order.id == order_id).first()
    order.status = OrderStatus.cancelled
    db.commit()
    db.refresh(payment)
    return payment

# User: get payment status for their order
@router.get("/{order_id}",response_model=PaymentResponse)
def get_payment(order_id: int, db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id,Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404,detail="Order not found")
    if not order.payment:
        raise HTTPException(status_code=404,detail="No payment found for this order")
    return order.payment    
