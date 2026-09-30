"""
Base classes for the Oculus fraud rule engine.

FraudRule ABC: All rules inherit from this.
RuleResult dataclass: Standardized output from every rule evaluation.
RuleTier enum: Categorizes rules by latency budget and execution mode.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class RuleTier(Enum):
    TIER_1_DETERMINISTIC = 1   # <10ms, in-process, no network calls
    TIER_2_SUPERVISED_ML = 2   # async, post-authorization (future)
    TIER_3_UNSUPERVISED = 3    # batch/offline (future)


@dataclass
class RuleResult:
    rule_name: str
    triggered: bool
    risk_contribution: float   # 0.0 to 1.0, weighted partial score
    reason: str
    tier: RuleTier


class FraudRule(ABC):
    name: str
    weight: float              # how much this rule contributes to final score
    tier: RuleTier = RuleTier.TIER_1_DETERMINISTIC

    @abstractmethod
    def evaluate(self, transaction, profile: dict) -> RuleResult:
        """
        Evaluate the rule against a transaction and user profile.

        profile is pre-fetched from Redis cache.
        Never make a network call or DB query inside evaluate().
        This method must complete in under 10ms.
        """
        ...
