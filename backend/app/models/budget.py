from datetime import datetime

from sqlalchemy import Column, Float, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.enums import gen_uuid


class TripBudgetSummary(Base):
    __tablename__ = "trip_budget_summary"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    trip_id = Column(UUID(as_uuid=False), ForeignKey("trips.id"), nullable=False)
    total_cost = Column(Float, nullable=False)
    cost_per_member = Column(Float, nullable=False)
    details = Column(Text, nullable=True)  # JSON string berisi rincian per komponen biaya
    calculated_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", back_populates="budgets")
