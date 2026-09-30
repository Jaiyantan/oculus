"""Pydantic schemas for review actions."""
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class ReviewActionCreate(BaseModel):
    reviewer_id: str
    to_status: str
    notes: Optional[str] = None


class ReviewActionResponse(BaseModel):
    id: UUID
    fraud_flag_id: UUID
    reviewer_id: str
    from_status: str
    to_status: str
    notes: Optional[str] = None
    acted_at: datetime

    class Config:
        from_attributes = True


class ReviewActionListResponse(BaseModel):
    actions: list[ReviewActionResponse]
    total: int
