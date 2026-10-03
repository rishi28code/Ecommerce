# E-Commerce Backend API

A backend REST API for an e-commerce application built using **FastAPI, PostgreSQL, SQLAlchemy, Redis, JWT, and Python**.

This project is primarily focused on learning and implementing real-world backend concepts such as authentication, authorization, database relationships, inventory management, Redis-based locking, and background task processing.

---

## 🚀 Tech Stack

- **Python**
- **FastAPI** - REST API framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM
- **Redis** - Distributed locking
- **JWT** - Authentication
- **bcrypt** - Password hashing
- **Pydantic** - Request/response validation
- **Uvicorn** - ASGI server
- **python-dotenv** - Environment variable management

---

## 📌 Features

### Authentication & Authorization

- User registration
- User login
- Password hashing using bcrypt
- JWT access token generation
- JWT token validation
- Authentication middleware
- Role-Based Access Control (RBAC)
- Admin and customer authorization

### Product Management

- Create products
- Retrieve all products
- Retrieve a specific product
- Update products
- Delete products
- Product inventory/quantity management

### Order Management

- Create orders
- Update orders
- Delete orders
- Order items
- Product inventory management
- Inventory restoration when applicable
- Database relationships between:
  - Users
  - Orders
  - Order Items
  - Products

### Redis-Based Product Locking

Redis is used to implement temporary locks when administrators access a product for editing.

The locking mechanism includes:

- Acquire product lock
- Lock ownership
- Lock expiration using TTL
- Release product lock
- Prevent another administrator from modifying a locked product

Current lock timeout:

```text
5 minutes
