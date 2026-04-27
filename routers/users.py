from fastapi import APIRouter,Depends,HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from auth import hash_password, verify_password, create_access_token, get_current_user
import models
from schemas import UserRegister,UserResponse,Token

router = APIRouter(prefix='/users',tags=['Users'])

# FOR DEVELOPMENT USE
@router.get("/users/all")
def get_all_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@router.delete("/user")
def remove_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    db.delete(user)
    db.commit()
    return {"msg": "User is Removed"}


# FOR PRODUCTION USE
@router.post("/register", response_model=UserResponse)
def register(data: UserRegister,db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == data.emaill).first():
        raise HTTPException(status_code=400,detail="Email already registered")
    user = models.User(email=data.email,hashed_password=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401,detail="Invalid Credentials")
    token = create_access_token(data={"sub": user.email})
    return {"access_token": token,"token_type":"bearer"}

@router.get("/me",response_model=UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@router.post("/register/admin")
def register_admin(email: str, password: str, admin: bool, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = models.User(
        email=email,
        hashed_password=hash_password(password),
        is_admin=admin
    )
    db.add(user)
    db.commit()
    return {"msg": "Admin user created"}

