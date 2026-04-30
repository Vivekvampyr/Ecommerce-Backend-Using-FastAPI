from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from auth import require_admin
from schemas import CategoryCreate, CategoryResponse
from models import Category

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("/",response_model=List[CategoryResponse])
def list_categories(db:Session=Depends(get_db)):
    return db.query(Category).all()

@router.get("/{category_id}",response_model=CategoryResponse)
def get_category(category_id: int,db:Session=Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404,detail="Category not found")
    return category

# Admin Only
@router.post("/",response_model=CategoryResponse)
def create_category(data: CategoryCreate, db:Session=Depends(get_db),admin=Depends(require_admin)):
    if db.query(Category).filter(Category.name == data.name).first():
        raise HTTPException(status_code=400,detail="Category already exists")
    category = Category(name=data.name,description=data.description)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.patch("/{category_id}")
def update_category(category_id: int, data: CategoryCreate , db:Session=Depends(get_db), admin=Depends(require_admin)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404,detail="Category not found")
    category.name = data.name
    category.description = data.description
    db.commit()
    db.refresh(category)
    return category

@router.delete("/{category_id}")
def delete_category(category_id: int, db:Session=Depends(get_db), admin=Depends(require_admin)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404,detail="Category not found")
    db.delete(category)
    db.commit()
    return {"msg":"Category deleted"}
