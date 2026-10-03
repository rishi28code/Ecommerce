from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import database_models
from models import UserCreate, UserLogin, UserResponse
from utils.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


# ✅ REGISTER
@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):

    # 🔹 check if user already exists
    existing_user = db.query(database_models.User).filter(
        database_models.User.email == user.email
    ).first()


    # if mail already exists then throw this error
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # 🔹 hash password
    hashed_password = hash_password(user.password)

    # 🔹 create user (role included from request)
    new_user = database_models.User(
        email=user.email,
        password=hashed_password,
        role=user.role   # ✅ RBAC enabled
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ✅ LOGIN
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(database_models.User).filter(
        database_models.User.email == user.email
    ).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid password")

    # 🔑 generate token (RBAC payload)
    token = create_access_token({
        "sub": db_user.email,
        "user_id": db_user.id,
        "role": db_user.role.value   # ⚠️ Enum → string
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }