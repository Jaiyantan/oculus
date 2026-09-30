"""
Score aggregation — combines individual rule contributions into a final risk score
and classifies into risk tiers.
"""
from config.risk_thresholds import RISK_THRESHOLDS


def aggregate_scores(transaction_id, results):
    """
    Aggregate rule results into a final risk assessment.

    Args:
        transaction_id: UUID of the transaction
        results: List of RuleResult objects from rule evaluations

    Returns:
        dict with risk_score, risk_tier, and per-rule breakdown
    """
    total_risk = min(sum(r.risk_contribution for r in results), 1.0)

    if total_risk >= RISK_THRESHOLDS["auto_block"]:
        tier = "auto_block"
    elif total_risk >= RISK_THRESHOLDS["flag_for_review"]:
        tier = "flag_for_review"
    elif total_risk >= RISK_THRESHOLDS["log_only"]:
        tier = "log_only"
    else:
        tier = "clean"

    return {
        "transaction_id": transaction_id,
        "risk_score": round(total_risk, 4),
        "risk_tier": tier,
        "rule_results": [
            {
                "rule_name": r.rule_name,
                "triggered": r.triggered,
                "risk_contribution": round(r.risk_contribution, 4),
                "reason": r.reason
            }
            for r in results
        ]
    }
