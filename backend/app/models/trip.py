from datetime import datetime

from sqlalchemy import Column, String, Integer, Enum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.enums import gen_uuid, TransportMode, TripStatus, MemberRole


class Trip(Base):
    __tablename__ = "trips"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    owner_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    destination_city = Column(String(255), nullable=False)
    duration_days = Column(Integer, nullable=False)
    departure_month_target = Column(DateTime, nullable=False)
    transport_mode = Column(Enum(TransportMode), nullable=False)
    status = Column(Enum(TripStatus), default=TripStatus.draft, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_trips")
    members = relationship("TripMember", back_populates="trip", cascade="all, delete-orphan")
    vehicle_groups = relationship("TripVehicleGroup", back_populates="trip", cascade="all, delete-orphan")
    hotels = relationship("TripHotel", back_populates="trip", cascade="all, delete-orphan")
    activities = relationship("TripActivity", back_populates="trip", cascade="all, delete-orphan")
    budgets = relationship("TripBudgetSummary", back_populates="trip", cascade="all, delete-orphan")
    installments = relationship("TripInstallment", back_populates="trip", cascade="all, delete-orphan")
    transport_items = relationship("TripTransport", back_populates="trip", cascade="all, delete-orphan")


class TripMember(Base):
    __tablename__ = "trip_members"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    trip_id = Column(UUID(as_uuid=False), ForeignKey("trips.id"), nullable=False)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    name = Column(String(255), nullable=False)  # selalu diisi
    origin_city = Column(String(255), nullable=False)
    role = Column(Enum(MemberRole), default=MemberRole.member, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", back_populates="members")
    user = relationship("User", foreign_keys=[user_id], back_populates="trip_memberships")
    vehicle_memberships = relationship("TripVehicleMember", back_populates="member", cascade="all, delete-orphan")
    installments = relationship("TripInstallment", back_populates="member", cascade="all, delete-orphan")
    transport = relationship("TripTransport", back_populates="member", cascade="all, delete-orphan")
