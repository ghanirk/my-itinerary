from datetime import datetime

from sqlalchemy import Column, String, Float, Enum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.enums import gen_uuid, TransportMode


class TripTransport(Base):
    """Harga transport per-anggota untuk moda non-mobil-pribadi (kereta/pesawat/travel/bis)."""
    __tablename__ = "trip_transport"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    trip_id = Column(UUID(as_uuid=False), ForeignKey("trips.id"), nullable=False)
    member_id = Column(UUID(as_uuid=False), ForeignKey("trip_members.id"), nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", back_populates="transport_items")
    member = relationship("TripMember", back_populates="transport")


class TripVehicleGroup(Base):
    """Satu kelompok kendaraan untuk moda mobil_pribadi, dipakai bareng oleh beberapa anggota."""
    __tablename__ = "trip_vehicle_groups"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    trip_id = Column(UUID(as_uuid=False), ForeignKey("trips.id"), nullable=False)
    total_cost = Column(Float, nullable=True)  # biaya total untuk kendaraan ini (bensin+tol)
    vehicle_label = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", back_populates="vehicle_groups")
    members = relationship("TripVehicleMember", back_populates="group", cascade="all, delete-orphan")


class TripVehicleMember(Base):
    """Tabel asosiasi many-to-many antara TripVehicleGroup dan TripMember."""
    __tablename__ = "trip_vehicle_members"

    group_id = Column(UUID(as_uuid=False), ForeignKey("trip_vehicle_groups.id"), primary_key=True)
    member_id = Column(UUID(as_uuid=False), ForeignKey("trip_members.id"), primary_key=True)

    group = relationship("TripVehicleGroup", back_populates="members")
    member = relationship("TripMember", back_populates="vehicle_memberships")


class PriceReference(Base):
    """Referensi harga transport per rute+moda, dikelola admin (Tahap 7)."""
    __tablename__ = "price_reference"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    mode = Column(Enum(TransportMode), nullable=False)
    origin_city = Column(String(255), nullable=False)
    destination_city = Column(String(255), nullable=False)
    estimated_price = Column(Float, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
