"""
Redis cache service.

Redis is used here for:
1. Caching order status for faster reads.
2. Simple API rate limiting.
"""

import json
import redis

from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def cache_order_status(order_id: int, data: dict, expire_seconds: int = 300) -> None:
    """Store order status in Redis with expiry."""
    redis_client.setex(f"order_status:{order_id}", expire_seconds, json.dumps(data))


def get_cached_order_status(order_id: int) -> dict | None:
    """Read cached order status from Redis if available."""
    raw_value = redis_client.get(f"order_status:{order_id}")
    if not raw_value:
        return None
    return json.loads(raw_value)


def check_rate_limit(client_ip: str, limit: int = 30, window_seconds: int = 60) -> bool:
    """
    Simple Redis rate limiter.

    Allows `limit` requests per `window_seconds` for each client IP.
    Returns True if request is allowed, False if blocked.
    """
    key = f"rate_limit:{client_ip}"
    current_count = redis_client.incr(key)

    if current_count == 1:
        redis_client.expire(key, window_seconds)

    return current_count <= limit
