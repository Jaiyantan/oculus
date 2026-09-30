"""BlacklistEntry model — created when fraud is confirmed, checked before rules run."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from db.base import Base


class BlacklistEntry(Base):
    __tablename__ = "blacklist_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entry_type = Column(String, nullable=False)  # 'user_id' | 'device_fingerprint' | 'ip_address'
    entry_value = Column(String, nullable=False)
    added_from_flag_id = Column(UUID(as_uuid=True), ForeignKey("fraud_flags.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("entry_type", "entry_value", name="uq_blacklist_type_value"),
    )
