"""
Health check route — GET /api/v1/health

Verifies database and Redis connectivity.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from api.deps import get_db, get_redis
from datetime import datetime, timezone

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health")
def health_check(
    db: Session = Depends(get_db),
    redis_client=Depends(get_redis),
):
    """Check the health of all system components."""
    result = {
        "status": "ok",
        "db": "unknown",
        "redis": "unknown",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Check database
    try:
        db.execute(text("SELECT 1"))
        result["db"] = "ok"
    except Exception as e:
        result["db"] = f"error: {str(e)}"
        result["status"] = "degraded"

    # Check Redis
    try:
        redis_client.ping()
        result["redis"] = "ok"
    except Exception as e:
        result["redis"] = f"error: {str(e)}"
        result["status"] = "degraded"

    return result
