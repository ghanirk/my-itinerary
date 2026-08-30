from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.enums import gen_uuid


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_premium_trial_used = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    places = relationship("Place", back_populates="creator")
    plans = relationship("Plan", back_populates="user")
    owned_trips = relationship("Trip", foreign_keys="Trip.owner_id", back_populates="owner")
    trip_memberships = relationship("TripMember", foreign_keys="TripMember.user_id", back_populates="user")
