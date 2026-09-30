"""
Amount Anomaly Rule — Tier-1 Deterministic

Detects statistically unusual transaction amounts using Z-score
against each user's individual rolling baseline (Welford's algorithm).
"""
import math
from .base import FraudRule, RuleResult, RuleTier
from .registry import register_rule


@register_rule
class AmountAnomalyRule(FraudRule):
    name = "amount_rule"
    weight = 0.40
    tier = RuleTier.TIER_1_DETERMINISTIC

    Z_SCORE_THRESHOLD = 2.5     # flag above 2.5 standard deviations
    MIN_HISTORY_COUNT = 5       # need at least 5 transactions to establish a baseline

    def evaluate(self, transaction, profile: dict) -> RuleResult:
        count = profile.get("amount_count", 0)
        mean = profile.get("amount_mean", 0.0)
        var = profile.get("amount_variance", 0.0)

        if count < self.MIN_HISTORY_COUNT:
            return RuleResult(
                self.name, False, 0.0,
                f"Insufficient history ({count} transactions), skipping amount baseline",
                self.tier
            )

        stddev = math.sqrt(var) if var > 0 else 1.0
        amount = float(transaction.amount) if hasattr(transaction, 'amount') else float(transaction.get('amount', 0))
        z_score = abs(amount - mean) / stddev

        if z_score < self.Z_SCORE_THRESHOLD:
            return RuleResult(
                self.name, False, 0.0,
                f"Z-score {z_score:.2f}, within normal range (baseline mean: ${mean:.2f})",
                self.tier
            )

        # Score scales with z-score, capped at rule weight
        contribution = min(self.weight * (z_score / (self.Z_SCORE_THRESHOLD * 2)), self.weight)

        return RuleResult(
            self.name, True, contribution,
            f"Z-score {z_score:.2f} (amount ${amount:.2f}, baseline mean ${mean:.2f})",
            self.tier
        )
