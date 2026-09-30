"""
Fraud Engine — the core orchestrator.

Evaluates all Tier-1 rules against a transaction and returns
the aggregated risk assessment.
"""
from .rules.registry import get_rules_by_tier
from .rules.base import RuleTier
from .scoring import aggregate_scores


class FraudEngine:
    """
    Hot path entry point. Must complete in under 10ms.
    No network calls. No DB queries.
    Profile data comes from Redis cache only.
    """

    def evaluate_tier1(self, transaction, profile: dict) -> dict:
        """
        Evaluate all Tier-1 deterministic rules against the transaction.

        Args:
            transaction: Transaction object or dict with transaction data
            profile: Pre-fetched user profile from Redis cache

        Returns:
            dict with risk_score, risk_tier, and per-rule breakdown
        """
        rules = get_rules_by_tier(RuleTier.TIER_1_DETERMINISTIC)
        results = [rule.evaluate(transaction, profile) for rule in rules]

        # Get transaction ID (handles both object and dict)
        tx_id = getattr(transaction, 'id', None) or (
            transaction.get('id') if isinstance(transaction, dict) else None
        )

        return aggregate_scores(tx_id, results)
