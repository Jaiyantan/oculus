"""FraudFlag model — one row per flagged transaction (risk_score >= 0.20)."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from db.base import Base


class FraudFlag(Base):
    __tablename__ = "fraud_flags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=False)
    risk_score = Column(Numeric(5, 4), nullable=False)
    risk_tier = Column(String, nullable=False)  # 'auto_block' | 'flag_for_review' | 'log_only'
    rule_results = Column(JSONB, nullable=False)
    review_status = Column(String, default="pending_review", index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    transaction = relationship("Transaction", back_populates="fraud_flag")
    review_actions = relationship("ReviewAction", back_populates="fraud_flag", order_by="ReviewAction.acted_at.desc()")
