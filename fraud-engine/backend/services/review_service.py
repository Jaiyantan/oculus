"""
Review service — enforces the state machine for fraud flag review transitions.

Valid transitions:
    PENDING_REVIEW -> CONFIRMED_FRAUD | CLEARED | ESCALATED
    CONFIRMED_FRAUD -> PENDING_REVIEW (reopen)
    CLEARED -> PENDING_REVIEW (reopen)
    ESCALATED -> CONFIRMED_FRAUD | CLEARED

Invalid transitions return HTTP 422.
"""
from sqlalchemy.orm import Session
from models.fraud_flag import FraudFlag
from models.review_action import ReviewAction
from models.blacklist import BlacklistEntry
from services.profile_cache import set_user_blacklisted
from datetime import datetime, timezone

VALID_TRANSITIONS = {
    "pending_review": {"confirmed_fraud", "cleared", "escalated"},
    "confirmed_fraud": {"pending_review"},
    "cleared": {"pending_review"},
    "escalated": {"confirmed_fraud", "cleared"},
}


def validate_transition(current: str, target: str) -> bool:
    """Check if a status transition is valid per the state machine."""
    return target in VALID_TRANSITIONS.get(current, set())


def perform_review_action(
    db: Session,
    redis_client,
    flag_id: str,
    reviewer_id: str,
    to_status: str,
    notes: str = None
) -> dict:
    """
    Execute a review action with state machine validation.

    Args:
        db: Database session
        redis_client: Redis connection
        flag_id: UUID of the fraud flag
        reviewer_id: Reviewer identifier
        to_status: Target status
        notes: Optional reviewer notes

    Returns:
        dict with transition details

    Raises:
        ValueError: If the flag is not found
        PermissionError: If the transition is invalid
    """
    flag = db.query(FraudFlag).filter(FraudFlag.id == flag_id).first()
    if not flag:
        raise ValueError(f"Fraud flag {flag_id} not found")

    current_status = flag.review_status

    if not validate_transition(current_status, to_status):
        raise PermissionError(
            f"Invalid transition: {current_status} -> {to_status}. "
            f"Valid transitions from '{current_status}': {VALID_TRANSITIONS.get(current_status, set())}"
        )

    # Create the audit trail entry (append-only, never updated)
    action = ReviewAction(
        fraud_flag_id=flag.id,
        reviewer_id=reviewer_id,
        from_status=current_status,
        to_status=to_status,
        notes=notes,
    )
    db.add(action)

    # Update the flag status
    flag.review_status = to_status
    flag.updated_at = datetime.now(timezone.utc)

    # If confirmed as fraud, auto-blacklist the user
    if to_status == "confirmed_fraud":
        _auto_blacklist(db, redis_client, flag)

    db.commit()
    db.refresh(action)

    return {
        "id": str(action.id),
        "fraud_flag_id": str(action.fraud_flag_id),
        "reviewer_id": action.reviewer_id,
        "from_status": action.from_status,
        "to_status": action.to_status,
        "notes": action.notes,
        "acted_at": action.acted_at,
    }


def _auto_blacklist(db: Session, redis_client, flag: FraudFlag):
    """
    When fraud is confirmed, automatically blacklist the user.
    Writes to both PostgreSQL (permanent record) and Redis (fast lookup).
    """
    transaction = flag.transaction
    if not transaction:
        return

    # Check if already blacklisted
    existing = db.query(BlacklistEntry).filter(
        BlacklistEntry.entry_type == "user_id",
        BlacklistEntry.entry_value == transaction.user_id
    ).first()

    if not existing:
        entry = BlacklistEntry(
            entry_type="user_id",
            entry_value=transaction.user_id,
            added_from_flag_id=flag.id,
        )
        db.add(entry)

        # Also set in Redis for fast hot-path lookup
        if redis_client:
            set_user_blacklisted(redis_client, transaction.user_id)
