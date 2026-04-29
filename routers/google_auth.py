from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config as StarletteConfig
from database import get_db
from auth import create_access_token
from config import settings
from utils.limiter import limiter
import models

router = APIRouter(prefix="/auth", tags=["OAuth"])

# OAuth Client Setup
starlette_config = StarletteConfig(environ={
    "GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID,
    "GOOGLE_CLIENT_SECRET": settings.GOOGLE_CLIENT_SECRET,
})

oauth = OAuth(starlette_config)
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# Redirect User to Google Login
@router.get("/google")
@limiter.limit("20/minute")
async def google_login(request: Request):
    return await oauth.google.authorize_redirect(request,settings.GOOGLE_REDIRECT_URI)

# Google redirect back here with code
@router.get("/google/callback")
async def google_callback(request: Request,db:Session=Depends(get_db)):
    """
    Google sends user back here after login.
    We exchange the code for user info and return a JWT.
    """
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception:
        raise HTTPException(status_code=400,detail="Google OAuth Failed - try again")
    
    # Get user info from google
    user_info = token.get("userinfo")
    if not user_info:
        raise HTTPException(status_code=400,detail="Could not fetch user from Google")
    
    google_id = user_info['sub']
    email = user_info['email']
    avatar = user_info.get('picture')

    # Find or create user
    user = db.query(models.User).filter(models.User.google_id == google_id).first()
    if not user:
        # Check if email already exists via normal signup
        user = db.query(models.User).filter(models.User.email == email).first()
        if user:
            user.google_id = google_id
            user.avatar = avatar
            db.commit()
        else:
            # Brand new user via Google
            user = models.User(
                email=email,
                google_id=google_id,
                avatar=avatar,
                hashed_password=None
            )
            db.add(user)
            db.commit()
            db.refresh(user)
    # Issue our own JWT same as normal login
    access_token = create_access_token(data={"sub":user.email})
    # In production: redirect to your frontend with the token
    # return RedirectResponse(f"https://yourfrontend.com/oauth?token={access_token}")

    # For now — return token directly (useful for Swagger testing)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "avatar": user.avatar,
            "is_admin": user.is_admin,
        }
    }