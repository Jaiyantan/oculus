"""
Redis profile cache service.

All Tier-1 rules read exclusively from these cached user profiles.
Never from PostgreSQL on the hot path.

Uses Welford's online algorithm for running mean/variance updates.
"""
import json
from datetime import datetime, timezone


# Fallback in-memory cache if Redis is unavailable
_memory_cache = {
    "user:user_demo_alice:amount_stats": json.dumps({"mean": 48.0, "variance": 144.0, "count": 50, "m2": 7200.0}),
    "user:user_demo_alice:last_location": json.dumps({"lat": 40.7128, "lon": -74.0060, "timestamp": datetime.now(timezone.utc).isoformat()}),
    "user:user_demo_bob:amount_stats": json.dumps({"mean": 320.0, "variance": 6400.0, "count": 50, "m2": 320000.0}),
    "user:user_demo_bob:last_location": json.dumps({"lat": 51.5074, "lon": -0.1278, "timestamp": datetime.now(timezone.utc).isoformat()}),
    "user:user_demo_carol:amount_stats": json.dumps({"mean": 1200.0, "variance": 90000.0, "count": 50, "m2": 4500000.0}),
    "user:user_demo_carol:last_location": json.dumps({"lat": 35.6762, "lon": 139.6503, "timestamp": datetime.now(timezone.utc).isoformat()}),
}

def _cache_get(redis_client, key: str):
    if redis_client:
        try:
            return redis_client.get(key)
        except Exception:
            pass
    return _memory_cache.get(key)

def _cache_set(redis_client, key: str, val: str, ttl: int = None):
    _memory_cache[key] = str(val)
    if redis_client:
        try:
            if ttl:
                redis_client.setex(key, ttl, val)
            else:
                redis_client.set(key, val)
        except Exception:
            pass

def _cache_incr(redis_client, key: str):
    curr = int(_memory_cache.get(key, 0)) + 1
    _memory_cache[key] = curr
    if redis_client:
        try:
            redis_client.incr(key)
        except Exception:
            pass
    return curr

def get_user_profile(redis_client, user_id: str) -> dict:
    """
    Fetch the complete user profile from Redis cache (or in-memory demo fallback).
    Returns a dict ready for rule evaluation.
    """
    profile = {}

    # Velocity count
    velocity_key = f"user:{user_id}:velocity_count"
    velocity = _cache_get(redis_client, velocity_key)
    profile["velocity_count"] = int(velocity) if velocity else 0

    # Last known location
    location_key = f"user:{user_id}:last_location"
    location = _cache_get(redis_client, location_key)
    if location:
        try:
            profile["last_location"] = json.loads(location) if isinstance(location, str) else location
        except Exception:
            profile["last_location"] = None
    else:
        profile["last_location"] = None

    # Amount statistics (rolling mean, variance, count)
    stats_key = f"user:{user_id}:amount_stats"
    stats = _cache_get(redis_client, stats_key)
    if stats:
        try:
            stats_data = json.loads(stats) if isinstance(stats, str) else stats
            profile["amount_mean"] = stats_data.get("mean", 0.0)
            profile["amount_variance"] = stats_data.get("variance", 0.0)
            profile["amount_count"] = stats_data.get("count", 0)
        except Exception:
            profile["amount_mean"] = 0.0
            profile["amount_variance"] = 0.0
            profile["amount_count"] = 0
    else:
        profile["amount_mean"] = 0.0
        profile["amount_variance"] = 0.0
        profile["amount_count"] = 0

    # Blacklist check
    blacklist_key = f"user:{user_id}:blacklisted"
    profile["is_blacklisted"] = _cache_get(redis_client, blacklist_key) == "1"

    return profile


def update_profile_after_transaction(redis_client, user_id: str, transaction, current_stats: dict):
    """
    Update the user's Redis profile after a transaction is processed.
    Called after the response is returned to avoid adding latency to the hot path.

    Args:
        redis_client: Redis connection
        user_id: User identifier
        transaction: Transaction object
        current_stats: Current amount_stats from the profile
    """
    # 1. Increment velocity counter (sliding window via TTL)
    velocity_key = f"user:{user_id}:velocity_count"
    _cache_incr(redis_client, velocity_key)

    # 2. Update last known location
    lat = getattr(transaction, 'latitude', None)
    lon = getattr(transaction, 'longitude', None)
    if isinstance(transaction, dict):
        lat = transaction.get('latitude')
        lon = transaction.get('longitude')

    if lat and lon:
        _cache_set(
            redis_client,
            f"user:{user_id}:last_location",
            json.dumps({
                "lat": float(lat),
                "lon": float(lon),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }),
            ttl=3600
        )

    # 3. Update rolling amount stats using Welford's online algorithm
    amount = float(getattr(transaction, 'amount', 0))
    if isinstance(transaction, dict):
        amount = float(transaction.get('amount', 0))

    new_stats = welford_update(current_stats, amount)
    _cache_set(
        redis_client,
        f"user:{user_id}:amount_stats",
        json.dumps(new_stats),
        ttl=86400
    )


def welford_update(stats: dict, new_value: float) -> dict:
    """
    Welford's online algorithm for computing running mean and variance.
    Single-pass, numerically stable, O(1) per update.

    Args:
        stats: dict with 'mean', 'variance', 'count', 'm2' keys
        new_value: New observation

    Returns:
        Updated stats dict
    """
    count = stats.get("count", 0) + 1
    old_mean = stats.get("mean", 0.0)
    old_m2 = stats.get("m2", 0.0)

    delta = new_value - old_mean
    new_mean = old_mean + delta / count
    delta2 = new_value - new_mean
    new_m2 = old_m2 + delta * delta2

    new_variance = new_m2 / count if count > 1 else 0.0

    return {
        "mean": new_mean,
        "variance": new_variance,
        "count": count,
        "m2": new_m2
    }


def set_user_blacklisted(redis_client, user_id: str):
    """Mark a user as blacklisted in the cache (permanent, no TTL)."""
    _cache_set(redis_client, f"user:{user_id}:blacklisted", "1")
