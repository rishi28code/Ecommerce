from redis.redis_client import redis_client

LOCK_TIMEOUT = 300

def acquire_lock(product_id: int, user_id: int):

    lock_key = f"product:{product_id}:lock"

    return redis_client.set(
        lock_key,
        user_id,
        nx=True,
        ex=LOCK_TIMEOUT
    )


def release_lock(product_id: int):

    lock_key = f"product:{product_id}:lock"

    redis_client.delete(lock_key)


def get_lock_owner(product_id: int):

    lock_key = f"product:{product_id}:lock"

    return redis_client.get(lock_key)