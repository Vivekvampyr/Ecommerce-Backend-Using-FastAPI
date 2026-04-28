from fastapi import FastAPI
from database import engine, Base
from routers import shopping, users,cart

Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-commerce API")

app.include_router(shopping.router)
app.include_router(users.router)
app.include_router(cart.router)


