"""Pydantic schemas for transaction request/response."""
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class TransactionCreate(BaseModel):
    user_id: str
    amount: float = Field(gt=0)
    currency: str = Field(default="USD", max_length=3)
    merchant_id: Optional[str] = None
    merchant_category: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    device_fingerprint: Optional[str] = None
    ip_address: Optional[str] = None


class RuleResultSchema(BaseModel):
    rule_name: str
    triggered: bool
    risk_contribution: float
    reason: str


class TransactionResponse(BaseModel):
    transaction_id: UUID
    risk_score: float
    risk_tier: str
    rule_results: list[RuleResultSchema]
    flag_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class TransactionDetail(BaseModel):
    id: UUID
    user_id: str
    amount: float
    currency: str
    merchant_id: Optional[str] = None
    merchant_category: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    device_fingerprint: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
