from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.enums import gen_uuid


class TripActivity(Base):
    __tablename__ = "trip_activities"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    trip_id = Column(UUID(as_uuid=False), ForeignKey("trips.id"), nullable=False)
    place_id = Column(UUID(as_uuid=False), ForeignKey("places.id"), nullable=False)
    day_index = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", back_populates="activities")
    place = relationship("Place")
