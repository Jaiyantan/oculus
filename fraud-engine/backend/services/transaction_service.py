"""
Transaction service — orchestrates the full transaction processing pipeline.

Flow:
1. Check blacklist (Redis)
2. Fetch user profile (Redis)
3. Run Tier-1 rules (in-process, <10ms)
4. Write transaction to PostgreSQL
5. Create fraud flag if risk_score >= log_only threshold
6. Fire notification if auto_block
7. Update Redis profile (async, after response)
"""
from sqlalchemy.orm import Session
from models.transaction import Transaction
from models.fraud_flag import FraudFlag
from core.engine import FraudEngine
from services.profile_cache import get_user_profile, update_profile_after_transaction
from notifications.aws_notifier import publish_high_risk_alert
from config.risk_thresholds import RISK_THRESHOLDS


engine = FraudEngine()


def process_transaction(db: Session, redis_client, tx_data: dict) -> dict:
    """
    Full transaction processing pipeline.

    Args:
        db: Database session
        redis_client: Redis connection
        tx_data: Transaction data dict

    Returns:
        dict with transaction_id, risk_score, risk_tier, rule_results, and optional flag_id
    """
    user_id = tx_data["user_id"]

    # Step 1: Check blacklist
    profile = get_user_profile(redis_client, user_id)

    if profile.get("is_blacklisted"):
        # Blacklisted users get auto-blocked immediately
        return _handle_blacklisted_transaction(db, tx_data)

    # Step 2: Create transaction record
    transaction = Transaction(
        user_id=user_id,
        amount=tx_data["amount"],
        currency=tx_data.get("currency", "USD"),
        merchant_id=tx_data.get("merchant_id"),
        merchant_category=tx_data.get("merchant_category"),
        latitude=tx_data.get("latitude"),
        longitude=tx_data.get("longitude"),
        device_fingerprint=tx_data.get("device_fingerprint"),
        ip_address=tx_data.get("ip_address"),
    )
    db.add(transaction)
    db.flush()  # Get the ID without committing

    # Step 3: Run Tier-1 rules
    evaluation = engine.evaluate_tier1(transaction, profile)

    # Step 4: Create fraud flag if score meets threshold
    flag_id = None
    if evaluation["risk_score"] >= RISK_THRESHOLDS["log_only"]:
        fraud_flag = FraudFlag(
            transaction_id=transaction.id,
            risk_score=evaluation["risk_score"],
            risk_tier=evaluation["risk_tier"],
            rule_results=evaluation["rule_results"],
            review_status="pending_review" if evaluation["risk_tier"] != "log_only" else "log_only",
        )
        db.add(fraud_flag)
        db.flush()
        flag_id = fraud_flag.id

    db.commit()

    # Step 5: Fire notification if auto_block (after commit, non-blocking)
    if evaluation["risk_tier"] == "auto_block":
        try:
            publish_high_risk_alert(
                transaction_id=str(transaction.id),
                risk_score=evaluation["risk_score"],
                risk_tier=evaluation["risk_tier"],
                user_id=user_id,
                rule_results=evaluation["rule_results"],
            )
        except Exception as e:
            print(f"[NOTIFICATION] Failed to send alert: {e}")

    # Step 6: Update Redis profile (after response, non-blocking)
    try:
        current_stats = {
            "mean": profile.get("amount_mean", 0.0),
            "variance": profile.get("amount_variance", 0.0),
            "count": profile.get("amount_count", 0),
            "m2": profile.get("amount_count", 0) * profile.get("amount_variance", 0.0),
        }
        update_profile_after_transaction(redis_client, user_id, transaction, current_stats)
    except Exception as e:
        print(f"[CACHE UPDATE] Failed: {e}")

    return {
        "transaction_id": str(transaction.id),
        "risk_score": evaluation["risk_score"],
        "risk_tier": evaluation["risk_tier"],
        "rule_results": evaluation["rule_results"],
        "flag_id": str(flag_id) if flag_id else None,
    }


def _handle_blacklisted_transaction(db: Session, tx_data: dict) -> dict:
    """Handle a transaction from a blacklisted user — auto-block with maximum score."""
    transaction = Transaction(
        user_id=tx_data["user_id"],
        amount=tx_data["amount"],
        currency=tx_data.get("currency", "USD"),
        merchant_id=tx_data.get("merchant_id"),
        merchant_category=tx_data.get("merchant_category"),
        latitude=tx_data.get("latitude"),
        longitude=tx_data.get("longitude"),
        device_fingerprint=tx_data.get("device_fingerprint"),
        ip_address=tx_data.get("ip_address"),
    )
    db.add(transaction)
    db.flush()

    rule_results = [
        {
            "rule_name": "blacklist_check",
            "triggered": True,
            "risk_contribution": 1.0,
            "reason": f"User {tx_data['user_id']} is blacklisted"
        }
    ]

    fraud_flag = FraudFlag(
        transaction_id=transaction.id,
        risk_score=1.0,
        risk_tier="auto_block",
        rule_results=rule_results,
        review_status="auto_blocked",
    )
    db.add(fraud_flag)
    db.flush()

    db.commit()

    return {
        "transaction_id": str(transaction.id),
        "risk_score": 1.0,
        "risk_tier": "auto_block",
        "rule_results": rule_results,
        "flag_id": str(fraud_flag.id),
    }
