"""
FastAPI dependencies — database session and Redis client injection.
"""
import redis
from db.session import get_db as _get_db
from config.settings import get_settings


def get_db():
    """Yield a database session."""
    yield from _get_db()


_redis_client = None


def get_redis():
    """Return a Redis client (singleton) or None if Redis is unreachable."""
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        try:
            client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_timeout=0.3,
                socket_connect_timeout=0.3,
            )
            client.ping()
            _redis_client = client
        except Exception:
            # Redis is not running locally; profile_cache will use its in-memory fallback
            _redis_client = None
    return _redis_client
