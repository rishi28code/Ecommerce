# get all (with filtration based on user_id), so that we can get which user has how many orders; fields (id,user_id, no need of 'createds_at')

# post (the user can create an order like [{productId:quantity},{productId:quantity}]) ; user_id, array of objects

# put api to update any specifc order ; can only edit the array of objects containing {productId:quantity}

# delete api with order id,

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

import database_models
from models import OrderItemCreate, OrderResponse, OrderCreate
from database import get_db

#  RBAC dependencies
from dependencies.auth import get_current_user, require_customer

# importing email function 
from services.email_service import (
    send_order_confirmation_email
)

router = APIRouter(prefix="/orders", tags=["Orders"])


#  get all (with filtration based on user_id), so that we can get which user has how many orders; fields (id,user_id, no need of 'createds_at')
@router.get("/", response_model=List[OrderResponse])
def get_orders(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

   #  if user is admin we show all orders
    if current_user["role"] == "admin" :

        orders = db.query(
            database_models.Order
        ).all()

    # if user is customer then we will only his orders
    elif current_user["role"] == "customer" :
        orders = db.query(
            database_models.Order
        ).filter(
            database_models.Order.user_id == current_user["id"]
        ).all()

    # other roles not allowed
    else:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view orders"
        )

    return orders



@router.post("/", response_model=OrderResponse)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks,
    current_user = Depends(require_customer)
):

    try:

        # =========================
        # GET ALL PRODUCT IDS
        # =========================
        product_ids = [
            item.product_id
            for item in order.items
        ]

        # =========================
        # FETCH ALL PRODUCTS ONCE
        # =========================
        products = db.query(
            database_models.Product
        ).filter(
            database_models.Product.id.in_(product_ids)
        ).all()

        # =========================
        # CONVERT TO DICTIONARY
        # =========================
        products_map = {
            product.id: product
            for product in products
        }

        # =========================
        # VALIDATE PRODUCTS
        # =========================
        for item in order.items:

            db_product = products_map.get(
                item.product_id
            )

            # product not found
            if not db_product:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product {item.product_id} not found"
                )

            # invalid quantity
            if item.quantity <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Quantity must be greater than 0"
                )

            # insufficient stock
            if item.quantity > db_product.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Only {db_product.quantity} items available for {db_product.name}"
                )

        # =========================
        # CREATE MAIN ORDER
        # =========================
        db_order = database_models.Order(
            user_id=current_user["id"],
            description=order.description
        )

        db.add(db_order)

        # flush gets ID without commit
        db.flush()

        # =========================
        # CREATE ORDER ITEMS
        # =========================
        for item in order.items:

            db_product = products_map.get(
                item.product_id
            )

            # reduce inventory
            db_product.quantity -= item.quantity

            # create order item
            db_order_item = database_models.OrderItem(
                order_id=db_order.id,
                product_id=item.product_id,
                quantity=item.quantity
            )

            db.add(db_order_item)

        # =========================
        # SINGLE COMMIT
        # =========================
        db.commit()

        # refresh final order
        db.refresh(db_order)

        # run email task after response - (Background Task)
        background_tasks.add_task(
            send_order_confirmation_email, 
            current_user["email"],
            db_order.id
        )

        return db_order

    except Exception as e:

        db.rollback()

        raise e



# put api order
@router.put("/{id}", response_model=OrderResponse)
def update_order(
    id: int,
    updated_order: OrderCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_customer)
):

    try:

        # =========================
        # FIND ORDER
        # =========================
        db_order = db.query(database_models.Order).filter(
            database_models.Order.id == id,
            database_models.Order.user_id == current_user["id"]
        ).first()

        if not db_order:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        # =========================
        # GET ALL PRODUCT IDS
        # =========================
        product_ids = [item.product_id for item in updated_order.items]

        # =========================
        # FETCH ALL PRODUCTS IN ONE QUERY
        # =========================
        products = db.query(database_models.Product).filter(
            database_models.Product.id.in_(product_ids)
        ).all()

        products_map = {
            product.id: product
            for product in products
        }

        # =========================
        # FETCH EXISTING ORDER ITEMS
        # =========================
        existing_order_items = db.query(
            database_models.OrderItem
        ).filter(
            database_models.OrderItem.order_id == id
        ).all()

        existing_items_map = {
            item.product_id: item
            for item in existing_order_items
        }

        # =========================
        # PROCESS UPDATED ITEMS
        # =========================
        for item in updated_order.items:

            db_product = products_map.get(
                item.product_id
            )

            if not db_product:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product {item.product_id} not found"
                )

            if item.quantity <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Quantity must be greater than 0"
                )

            existing_item = existing_items_map.get(
                item.product_id
            )

            # =========================
            # UPDATE EXISTING ITEM
            # =========================
            if existing_item:

                difference = (
                    item.quantity -
                    existing_item.quantity
                )

                if difference > 0:

                    if difference > db_product.quantity:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Only {db_product.quantity} extra items available for {db_product.name}"
                        )

                    db_product.quantity -= difference

                elif difference < 0:

                    db_product.quantity += abs(
                        difference
                    )

                existing_item.quantity = (
                    item.quantity
                )

            # =========================
            # ADD NEW PRODUCT
            # =========================
            else:

                if item.quantity > db_product.quantity:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Only {db_product.quantity} items available for {db_product.name}"
                    )

                db_product.quantity -= item.quantity

                new_item = (
                    database_models.OrderItem(
                        order_id=id,
                        product_id=item.product_id,
                        quantity=item.quantity
                    )
                )

                db.add(new_item)

        # =========================
        # UPDATE DESCRIPTION
        # =========================
        db_order.description = (
            updated_order.description
        )

        # =========================
        # SAVE CHANGES
        # =========================
        db.commit()

        db.refresh(db_order)

        return db_order

    except Exception:

        db.rollback()

        raise


# delete api

@router.delete("/{id}")
def delete_order(
    id: int,
    db: Session = Depends(get_db)
):

    try:

        db_order = db.query(
            database_models.Order
        ).filter(
            database_models.Order.id == id
        ).first()

        if not db_order:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        order_items = db.query(
            database_models.OrderItem
        ).filter(
            database_models.OrderItem.order_id == id
        ).all()

        # restore inventory
        for item in order_items:

            product = db.query(
                database_models.Product
            ).filter(
                database_models.Product.id == item.product_id
            ).first()

            product.quantity += item.quantity
            # delete order items one by one
            db.delete(item)
        
        
            

        # delete order
        db.delete(db_order)

        db.commit()

        return {
            "message": "Order deleted successfully"
        }

    except Exception:
        db.rollback()
        raise

