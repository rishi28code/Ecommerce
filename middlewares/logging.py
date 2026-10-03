from fastapi import Request
import time

# This is a middleware function
# It runs for EVERY incoming request before it reaches your API
async def log_requests(request: Request, call_next):

    # ⏱️ Step 1: Start timer when request enters middleware
    start_time = time.time()

    # 🟢 Step 2: Log incoming request details
    # request.method → GET, POST, PUT, DELETE
    # request.url → full URL of the API being called
    print(f"Request: {request.method} {request.url}")

    # 🔵 Step 3: Pass request to the actual API route
    # call_next(request) → this sends request to your endpoint (e.g., get_products)
    # IMPORTANT: Without this line, your API will NEVER run
    response = await call_next(request)

    # ⏱️ Step 4: Calculate how long the API took to process
    process_time = time.time() - start_time

    # 🟣 Step 5: Log response time (performance tracking)
    print(f"Completed in {process_time:.4f}s")

    # 🔁 Step 6: Return response back to client
    return response