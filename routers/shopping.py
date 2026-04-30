from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from database import get_db
from auth import require_admin
from schemas import ProductCreate, ProductResponse, ProductUpdate
from models import Product, Category, Review

router = APIRouter(prefix="/shopping", tags=["Shopping"])

@router.get("/products", response_model=List[ProductResponse])
def list_products(
    # ─── Search ─────────────────────────────────────────────
    search: Optional[str] = Query(None, description="Search by name or description"),

    # ─── Filters ────────────────────────────────────────────
    category_id: Optional[int] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    in_stock: Optional[bool] = Query(None, description="Only show in-stock items"),

    # ─── Sorting ────────────────────────────────────────────
    sort_by: Optional[str] = Query("id", enum=["id", "price", "name"]),
    order: Optional[str] = Query("asc", enum=["asc", "desc"]),

    # ─── Pagination ─────────────────────────────────────────
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),

    db: Session = Depends(get_db)
):
    query = db.query(Product)

    # Search — matches name OR description
    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%")
            )
        )

    # Category filter
    if category_id:
        query = query.filter(Product.category_id == category_id)

    # Price range filter
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    # Stock filter
    if in_stock is True:
        query = query.filter(Product.stock > 0)

    # Sorting
    sort_column = getattr(Product, sort_by, Product.id)
    query = query.order_by(sort_column.desc() if order == "desc" else sort_column.asc())

    # Pagination
    products = query.offset((page - 1) * limit).limit(limit).all()

    # ─── Attach avg rating + total reviews to each product ──
    for product in products:
        stats = db.query(
            func.avg(Review.rating),
            func.count(Review.id)
        ).filter(Review.product_id == product.id).first()
        product.average_rating = round(float(stats[0]), 1) if stats[0] else 0.0
        product.total_reviews = stats[1] if stats[1] else 0

    return products

# ─── Get single product ─────────────────────────────────────

@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Attach rating stats
    stats = db.query(
        func.avg(Review.rating),
        func.count(Review.id)
    ).filter(Review.product_id == product.id).first()
    product.average_rating = round(float(stats[0]), 1) if stats[0] else 0.0
    product.total_reviews = stats[1] if stats[1] else 0

    return product

# ─── Admin — add product ────────────────────────────────────

@router.post("/products", response_model=ProductResponse)
def add_product(data: ProductCreate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    if data.category_id:
        category = db.query(Category).filter(Category.id == data.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
    product = Product(
        name=data.name,
        description=data.description,
        price=data.price,
        stock=data.stock,
        category_id=data.category_id
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    # New product has no reviews yet
    product.average_rating = 0.0
    product.total_reviews = 0

    return product

# ─── Admin — edit product ───────────────────────────────────

@router.patch("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if data.category_id:
        category = db.query(Category).filter(Category.id == data.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    # Only update fields that were actually sent
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    # Reattach rating stats after update
    stats = db.query(
        func.avg(Review.rating),
        func.count(Review.id)
    ).filter(Review.product_id == product.id).first()
    product.average_rating = round(float(stats[0]), 1) if stats[0] else 0.0
    product.total_reviews = stats[1] if stats[1] else 0

    return product

# ─── Admin — delete product ─────────────────────────────────

@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"msg": "Product deleted"}