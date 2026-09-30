"""
Velocity Rule — Tier-1 Deterministic

Detects card-testing attack patterns by counting transactions
in a sliding 5-minute window per user.
"""
from .base import FraudRule, RuleResult, RuleTier
from .registry import register_rule


@register_rule
class VelocityRule(FraudRule):
    name = "velocity_rule"
    weight = 0.35
    tier = RuleTier.TIER_1_DETERMINISTIC

    WINDOW_SECONDS = 300    # 5-minute window
    THRESHOLD_COUNT = 5     # more than 5 transactions in window is suspicious

    def evaluate(self, transaction, profile: dict) -> RuleResult:
        count = profile.get("velocity_count", 0)

        if count <= self.THRESHOLD_COUNT:
            return RuleResult(
                self.name, False, 0.0,
                f"{count} transactions in {self.WINDOW_SECONDS}s window, under threshold",
                self.tier
            )

        # Score scales with how far over threshold, capped at 1.0
        excess_ratio = min((count - self.THRESHOLD_COUNT) / self.THRESHOLD_COUNT, 1.0)
        contribution = self.weight * excess_ratio

        return RuleResult(
            self.name, True, contribution,
            f"{count} transactions in {self.WINDOW_SECONDS}s, threshold is {self.THRESHOLD_COUNT}",
            self.tier
        )
