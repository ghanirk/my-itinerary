from datetime import datetime

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.enums import gen_uuid


class TripInstallment(Base):
    __tablename__ = "trip_installments"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    trip_id = Column(UUID(as_uuid=False), ForeignKey("trips.id"), nullable=False)
    member_id = Column(UUID(as_uuid=False), ForeignKey("trip_members.id"), nullable=False)
    month_index = Column(Integer, nullable=False)
    amount_due = Column(Float, nullable=False)
    amount_paid = Column(Float, default=0.0)
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", back_populates="installments")
    member = relationship("TripMember", back_populates="installments")
