from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from database import get_db
import database_models


# 🔹 Get authenticated user from middleware
def get_current_user(request: Request):

    if not hasattr(request.state, "user"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    return request.state.user


# 🔹 Admin-only access
def require_admin(
    current_user: dict = Depends(get_current_user)
):

    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return current_user


# customer-only access

def require_customer(
    current_user: dict = Depends(get_current_user)
):

    if current_user["role"] != "customer":
        raise HTTPException(
            status_code=403,
            detail="Customer access required"
        )

    return current_user






# Depends() Means
# "FastAPI, please manage this function for me."

# Including:

# arguments
# execution order
# lifecycle
# nested dependencies