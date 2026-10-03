from fastapi import Request
from fastapi.responses import JSONResponse
from utils.auth import verify_token

# Public routes that DON'T require authentication
PUBLIC_ROUTES = [
    "/auth/login",
    "/auth/register",
    "/docs",
    "/openapi.json"
]

async def simple_auth(request: Request, call_next):

    # Skip auth for public routes
    if request.url.path in PUBLIC_ROUTES:
        return await call_next(request)

    # Get Authorization header
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"detail": "Authorization header missing or invalid"}
        )

    # Extract token
    token = auth_header.split(" ")[1]

    # Verify token
    payload = verify_token(token)

    if payload is None:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid or expired token"}
        )

    # Attach authenticated user to request
    request.state.user = {
        "id": payload["user_id"],
        "email": payload["sub"],
        "role": payload["role"]
    }

    # Continue request flow
    response = await call_next(request)

    return response