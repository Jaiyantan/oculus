"""
Fraud flags routes — GET /api/v1/fraud-flags

Serves the reviewer console with flagged transactions and their details.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from api.deps import get_db
from models.fraud_flag import FraudFlag
from models.transaction import Transaction

router = APIRouter(prefix="/api/v1/fraud-flags", tags=["fraud-flags"])


@router.get("")
def list_fraud_flags(
    status: str = Query(None, description="Filter by review status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    List fraud flags with optional status filtering.
    Used by the reviewer console's 2-second polling loop.
    """
    query = db.query(FraudFlag).options(
        joinedload(FraudFlag.transaction)
    )

    if status:
        query = query.filter(FraudFlag.review_status == status)

    # Exclude log_only from default view (they're noise for reviewers)
    if not status:
        query = query.filter(FraudFlag.review_status != "log_only")

    total = query.count()
    flags = query.order_by(desc(FraudFlag.created_at)).offset(offset).limit(limit).all()

    return {
        "flags": [_serialize_flag(f) for f in flags],
        "total": total,
    }


@router.get("/{flag_id}")
def get_fraud_flag(
    flag_id: str,
    db: Session = Depends(get_db),
):
    """Get a single fraud flag with full transaction details and rule breakdown."""
    flag = db.query(FraudFlag).options(
        joinedload(FraudFlag.transaction),
        joinedload(FraudFlag.review_actions),
    ).filter(FraudFlag.id == flag_id).first()

    if not flag:
        raise HTTPException(status_code=404, detail="Fraud flag not found")

    result = _serialize_flag(flag)
    result["review_actions"] = [
        {
            "id": str(a.id),
            "reviewer_id": a.reviewer_id,
            "from_status": a.from_status,
            "to_status": a.to_status,
            "notes": a.notes,
            "acted_at": a.acted_at.isoformat() if a.acted_at else None,
        }
        for a in (flag.review_actions or [])
    ]

    return result


def _serialize_flag(flag: FraudFlag) -> dict:
    """Serialize a FraudFlag with its embedded transaction."""
    tx = flag.transaction
    return {
        "id": str(flag.id),
        "transaction_id": str(flag.transaction_id),
        "risk_score": float(flag.risk_score),
        "risk_tier": flag.risk_tier,
        "rule_results": flag.rule_results,
        "review_status": flag.review_status,
        "created_at": flag.created_at.isoformat() if flag.created_at else None,
        "updated_at": flag.updated_at.isoformat() if flag.updated_at else None,
        "transaction": {
            "id": str(tx.id),
            "user_id": tx.user_id,
            "amount": float(tx.amount),
            "currency": tx.currency,
            "merchant_id": tx.merchant_id,
            "merchant_category": tx.merchant_category,
            "latitude": float(tx.latitude) if tx.latitude else None,
            "longitude": float(tx.longitude) if tx.longitude else None,
            "device_fingerprint": tx.device_fingerprint,
            "ip_address": tx.ip_address,
            "created_at": tx.created_at.isoformat() if tx.created_at else None,
        } if tx else None,
    }
