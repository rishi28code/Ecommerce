from fastapi import FastAPI
from database import engine
import database_models

# middlewares
from middlewares.logging import log_requests
from middlewares.auth import simple_auth

# routes
from routes.product import router as product_router
from routes.auth import router as auth_router
from routes.order import router as order_router

app = FastAPI()

# register middlewares
app.middleware("http")(log_requests)
app.middleware("http")(simple_auth)

# include routes
app.include_router(product_router)
app.include_router(auth_router)
app.include_router(order_router)

# create tables
database_models.Base.metadata.create_all(bind=engine)