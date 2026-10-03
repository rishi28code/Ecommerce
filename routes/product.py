# product.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import database_models
from models import ProductCreate, ProductResponse
from database import get_db

# 🔐 RBAC dependencies
from dependencies.auth import get_current_user, require_admin

# record locking
from services.lock_service import (
    acquire_lock,
    release_lock,
    get_lock_owner
)

router = APIRouter(prefix="/products", tags=["Products"])


#  GET ALL PRODUCTS
@router.get("/", response_model=List[ProductResponse])
def get_products(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return db.query(database_models.Product).all()


#  GET SINGLE PRODUCT
@router.get("/{id}", response_model=ProductResponse)
def get_product(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):

    locked = acquire_lock(
        product_id=id,
        user_id=current_user["id"]
    )

    if not locked:

        lock_owner = get_lock_owner(id)

        raise HTTPException(
            status_code=409,
            detail=f"Product is already locked by user {lock_owner}"
        )

    db_product = db.query(
        database_models.Product
    ).filter(
        database_models.Product.id == id
    ).first()

    if not db_product:

        release_lock(id)

        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return db_product


#  CREATE PRODUCT (admin only)
@router.post("/", response_model=ProductResponse)
def create_product(
    product: ProductCreate,
    #Take JSON body and convert it into ProductCreate object

    db: Session = Depends(get_db),
    # get_db() returns generator object ,NOT actual DB session becaause of yield, so Depends(get_db) is used
    #creating database session 'db' by calling db

    current_user = Depends(require_admin)
):

    db_product = database_models.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        quantity=product.quantity
    )
    #Creates SQLAlchemy ORM object.
 
    db.add(db_product)
    #Marks object for insertion,Still not committed.

    db.commit()
    # Now SQLAlchemy sends SQL query:

    # INSERT INTO product (...)
    # VALUES (...)

    # Data saved in PostgreSQL.


    db.refresh(db_product)

    return db_product


# UPDATE PRODUCT (admin only)
@router.put("/{id}", response_model=ProductResponse)
def update_product(
    id: int,
    updated_product: ProductCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):

    try:

        lock_owner = get_lock_owner(id)

        if not lock_owner:
            raise HTTPException(
                status_code=409,
                detail="Product is not locked"
            )

        if str(lock_owner) != str(current_user["id"]):
            raise HTTPException(
                status_code=403,
                detail="You do not own the lock"
            )

        db_product = db.query(
            database_models.Product
        ).filter(
            database_models.Product.id == id
        ).first()

        if not db_product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        db_product.name = updated_product.name
        db_product.description = updated_product.description
        db_product.price = updated_product.price
        db_product.quantity = updated_product.quantity

        db.commit()

        db.refresh(db_product)

        return db_product

    except Exception:
        db.rollback()
        raise


# DELETE PRODUCT (admin only)
@router.delete("/{id}")
def delete_product(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    db_product = db.query(database_models.Product).filter(
        database_models.Product.id == id
    ).first()

    if not db_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    db.delete(db_product)
    db.commit()

    return {"message": "Product deleted successfully"}


# relese lock api
@router.post("/{id}/release-lock")
def release_product_lock(
    id: int,
    current_user = Depends(require_admin)
):

    lock_owner = get_lock_owner(id)

    if not lock_owner:
        raise HTTPException(
            status_code=404,
            detail="No active lock found"
        )

    if str(lock_owner) != str(current_user["id"]):
        raise HTTPException(
            status_code=403,
            detail="You do not own this lock"
        )

    release_lock(id)

    return {
        "message": "Lock released successfully"
    }