from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from database import engine, Base
from routers import shopping, users,cart,orders,coupons,google_auth,payments,categories,reviews
from starlette.middleware.sessions import SessionMiddleware
from config import settings

Base.metadata.create_all(bind=engine)
app = FastAPI(title="E-commerce API")

# MIDDLEWARE
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],               # lock this down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LIMITER SETUP
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler)


app.include_router(shopping.router)
app.include_router(users.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(coupons.router)
app.include_router(google_auth.router)
app.include_router(payments.router)
app.include_router(categories.router)
app.include_router(reviews.router)


