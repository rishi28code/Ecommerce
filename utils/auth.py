from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import Optional, Dict
from dotenv import load_dotenv

import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set")

ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 🔐 Password hashing
def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


# 🔑 Create JWT Token (RBAC READY)
def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    # add expiry
    to_encode.update({
        "exp": datetime.utcnow() + timedelta(minutes=30)
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# 🔍 Verify JWT Token (returns full payload)
def verify_token(token: str) -> Optional[Dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # optional: validate required fields
        if "sub" not in payload or "role" not in payload or "user_id" not in payload:
            return None

        return payload

    except JWTError:
        return None