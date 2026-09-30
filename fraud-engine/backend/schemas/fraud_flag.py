"""Pydantic schemas for fraud flags."""
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from .transaction import RuleResultSchema, TransactionDetail


class FraudFlagResponse(BaseModel):
    id: UUID
    transaction_id: UUID
    risk_score: float
    risk_tier: str
    rule_results: list[RuleResultSchema]
    review_status: str
    created_at: datetime
    updated_at: datetime
    transaction: Optional[TransactionDetail] = None

    class Config:
        from_attributes = True


class FraudFlagListResponse(BaseModel):
    flags: list[FraudFlagResponse]
    total: int
