"""
Review routes — PATCH /api/v1/fraud-flags/{flag_id}/review

Handles reviewer actions with state machine validation.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.deps import get_db, get_redis
from schemas.review import ReviewActionCreate
from services.review_service import perform_review_action
from models.review_action import ReviewAction
from sqlalchemy import desc

router = APIRouter(prefix="/api/v1", tags=["reviews"])


@router.patch("/fraud-flags/{flag_id}/review")
def review_fraud_flag(
    flag_id: str,
    action: ReviewActionCreate,
    db: Session = Depends(get_db),
    redis_client=Depends(get_redis),
):
    """
    Submit a review action for a fraud flag.

    Valid transitions are enforced by the state machine.
    Returns 422 if the transition is not valid.
    """
    try:
        result = perform_review_action(
            db=db,
            redis_client=redis_client,
            flag_id=flag_id,
            reviewer_id=action.reviewer_id,
            to_status=action.to_status,
            notes=action.notes,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/review-actions")
def list_review_actions(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    List all review actions (audit log).
    Append-only — never updated, never deleted.
    """
    total = db.query(ReviewAction).count()
    actions = (
        db.query(ReviewAction)
        .order_by(desc(ReviewAction.acted_at))
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "actions": [
            {
                "id": str(a.id),
                "fraud_flag_id": str(a.fraud_flag_id),
                "reviewer_id": a.reviewer_id,
                "from_status": a.from_status,
                "to_status": a.to_status,
                "notes": a.notes,
                "acted_at": a.acted_at.isoformat() if a.acted_at else None,
            }
            for a in actions
        ],
        "total": total,
    }
