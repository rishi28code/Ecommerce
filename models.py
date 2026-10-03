from pydantic import BaseModel
from typing import Literal
from datetime import datetime

# =========================
#  USER MODELS
# =========================

class UserCreate(BaseModel):
    email: str
    password: str
    role: Literal["user", "admin", "customer"]   # ✅ allowed for learning


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    role: str

    class Config:
        from_attributes = True


# =========================
#  PRODUCT MODELS
# =========================

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    quantity: int
   


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    quantity: int

    class Config:
        from_attributes = True


# Order Items models
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

# =========================
#  Order Models
# =========================
class OrderResponse(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    description: str
    items: list[OrderItemCreate]
    

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    
    description: str
    items : list[OrderItemCreate]
    


