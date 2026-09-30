"""ReviewAction model — append-only audit trail of every reviewer decision."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base


class ReviewAction(Base):
    __tablename__ = "review_actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fraud_flag_id = Column(UUID(as_uuid=True), ForeignKey("fraud_flags.id"), nullable=False, index=True)
    reviewer_id = Column(String, nullable=False)
    from_status = Column(String, nullable=False)
    to_status = Column(String, nullable=False)
    notes = Column(Text, nullable=True)
    acted_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationship
    fraud_flag = relationship("FraudFlag", back_populates="review_actions")
