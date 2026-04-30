from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from database import get_db
from auth import get_current_user, require_admin
from schemas import ReviewCreate, ReviewUpdate, ReviewResponse, ProductRatingSummary
from models import Review, Product, Order, OrderItem, OrderStatus
from utils.limiter import limiter

router = APIRouter(prefix="/reviews", tags=["Reviews"])

# Helpers
def has_purchased(user_id: int, product_id: int, db: Session) -> bool:
    # check if user has actually bought this product
    return db.query(Order).filter(Order.user_id == user_id,OrderItem.product_id == product_id,Order.status.in_([OrderStatus.paid,OrderStatus.shipped])).first() is not None

# Public

@router.get("product/{product_id}", response_model=List[ReviewResponse])
def get_product_reviews(
    product_id: int,
    rating: Optional[int] = Query(None, ge=1, le=5, description="Filter by star rating"),
    sort_by: Optional[str] = Query("created_at", enum=["created_at", "rating"]),
    order: Optional[str] = Query("desc", enum=["asc", "desc"]),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    query = db.query(Review).filter(Review.product_id == product_id)
    if rating:
        query = query.filter(Review.rating == rating)
    
    # Sorting
    sort_column = getattr(Review, sort_by, Review.created_at)
    query = query.order_by(sort_column.desc() if order == "desc" else sort_column.asc())

    # Pagination
    return query.offset((page - 1) * limit).limit(limit).all() 

@router.get("/product/{product_id}/summary",response_model=ProductRatingSummary)
def get_rating_summary(product_id: int, db:Session=Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404,detail="Product not found")
    reviews = db.query(Review).filter(Review.product_id == product_id).all()
    total = len(reviews)

    if total == 0:
        return ProductRatingSummary(
            product_id=product_id,
            average_rating=0.0,
            total_reviews=0,
            five_star=0, four_star=0, three_star=0, two_star=0, one_star=0
        )
    
    avg = round(sum(r.rating for r in reviews) / total, 1)

    return ProductRatingSummary(
        product_id=product_id,
        average_rating=avg,
        total_reviews=total,
        five_star=sum(1 for r in reviews if r.rating == 5),
        four_star=sum(1 for r in reviews if r.rating == 4),
        three_star=sum(1 for r in reviews if r.rating == 3),
        two_star=sum(1 for r in reviews if r.rating == 2),
        one_star=sum(1 for r in reviews if r.rating == 1),
    )

# Authenticated User Route
@router.post("/product/{product_id}",response_model=ReviewResponse)
def create_review(
    request: Request,
    product_id: int,
    data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Submit a review — user must have purchased and received the product.
    One review per product per user.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Must have purchased this product
    if not has_purchased(current_user.id, product_id, db):
        raise HTTPException(
            status_code=403,
            detail="You can only review products you have purchased"
        )

    # One review per product per user
    existing = db.query(Review).filter(
        Review.product_id == product_id,
        Review.user_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="You have already reviewed this product. Edit your existing review instead."
        )

    review = Review(
        product_id=product_id,
        user_id=current_user.id,
        rating=data.rating,
        title=data.title,
        body=data.body
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review

@router.patch("/{review_id}", response_model=ReviewResponse)
@limiter.limit("10/minute")
def update_review(
    request: Request,
    review_id: int,
    data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Edit your own review"""
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.user_id == current_user.id     # can only edit your own
    ).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(review, field, value)

    db.commit()
    db.refresh(review)
    return review

@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Delete your own review"""
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.user_id == current_user.id
    ).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    db.delete(review)
    db.commit()
    return {"msg": "Review deleted"}

@router.get("/me", response_model=List[ReviewResponse])
def my_reviews(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Get all reviews written by the current user"""
    return db.query(Review).filter(Review.user_id == current_user.id).all()

# Admin Route
@router.get("/all", response_model=List[ReviewResponse])
def all_reviews(
    product_id: Optional[int] = None,
    rating: Optional[int] = Query(None, ge=1, le=5),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Admin — view all reviews with optional filters"""
    query = db.query(Review)
    if product_id:
        query = query.filter(Review.product_id == product_id)
    if rating:
        query = query.filter(Review.rating == rating)
    return query.order_by(Review.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

@router.delete("/admin/{review_id}")
def admin_delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Admin — delete any review (e.g. abusive content)"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    db.delete(review)
    db.commit()
    return {"msg": "Review deleted by admin"}
