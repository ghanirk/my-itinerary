import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Enum, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())

class TransportMode(str, enum.Enum):
    kereta = "kereta"
    mobil_pribadi = "mobil_pribadi"
    pesawat = "pesawat"
    travel = "travel"
    bis = "bis"

class TripStatus(str, enum.Enum):
    draft = "draft"
    confirmed = "confirmed"

class MemberRole(str, enum.Enum):
    member = "member"
    admin = "admin"

class PlaceCategory(str, enum.Enum):
    kuliner = "kuliner"
    fun = "fun"
    sport = "sport"
    alam = "alam"


class SourceType(str, enum.Enum):
    manual = "manual"
    tiktok = "tiktok"
    youtube = "youtube"


class PlaceStatus(str, enum.Enum):
    draft = "draft"
    published = "published"


class PlanType(str, enum.Enum):
    manual = "manual"
    generated = "generated"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_premium_trial_used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    places = relationship("Place", back_populates="creator")
    plans = relationship("Plan", back_populates="user")
    is_admin = Column(Boolean, default=False, nullable=False)
    owned_trips = relationship("Trip", foreign_keys="Trip.owner_id", back_populates="owner")
    trip_memberships = relationship("TripMember", foreign_keys="TripMember.user_id", back_populates="user")


class Place(Base):
    __tablename__ = "places"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String(200), nullable=False)
    category = Column(Enum(PlaceCategory), nullable=False)
    price_min = Column(Integer, nullable=False, default=0)
    price_max = Column(Integer, nullable=False, default=0)
    gmaps_url = Column(String(500), nullable=False)
    city = Column(String(120), nullable=False, index=True)
    source_type = Column(Enum(SourceType), default=SourceType.manual, nullable=False)
    source_url = Column(String(500), nullable=True)
    photo_url = Column(String(500), nullable=True)
    opening_hours = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(Enum(PlaceStatus), default=PlaceStatus.published, nullable=False)
    created_by = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User", back_populates="places")
    reports = relationship("PlaceReport", back_populates="place")


class ImportLog(Base):
    """
    Satu baris = satu kali user berhasil memanggil AI lewat /places/import/preview.
    Dipakai buat rate limiting (kuota harian) supaya endpoint yang manggil Gemini
    ini gak bisa di-spam -- disimpan di DB (bukan counter in-memory) supaya tetap
    akurat walau server restart atau jalan di lebih dari satu worker/instance.
    """
    __tablename__ = "import_logs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True)
    source_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class PlaceReport(Base):
    __tablename__ = "place_reports"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    place_id = Column(UUID(as_uuid=False), ForeignKey("places.id"), nullable=False)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    place = relationship("Place", back_populates="reports")


class Plan(Base):
    __tablename__ = "plans"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=True)
    type = Column(Enum(PlanType), default=PlanType.manual, nullable=False)
    budget = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="plans")
    items = relationship("PlanItem", back_populates="plan", cascade="all, delete-orphan", order_by="PlanItem.order_index")


class PlanItem(Base):
    __tablename__ = "plan_items"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    plan_id = Column(UUID(as_uuid=False), ForeignKey("plans.id"), nullable=False)
    place_id = Column(UUID(as_uuid=False), ForeignKey("places.id"), nullable=False)
    order_index = Column(Integer, default=0)

    plan = relationship("Plan", back_populates="items")
    place = relationship("Place")


# ==================== TIER 2 - PREMIUM TRIP ====================

class Trip(Base):
    __tablename__ = "trips"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    owner_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    destination_city = Column(String(255), nullable=False)
    duration_days = Column(Integer, nullable=False)
    departure_month_target = Column(DateTime, nullable=False)  # tetap datetime
    transport_mode = Column(Enum(TransportMode), nullable=False)
    status = Column(Enum(TripStatus), default=TripStatus.draft, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relasi
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

class TripVehicleGroup(Base):
    __tablename__ = "trip_vehicle_groups"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    trip_id = Column(UUID(as_uuid=False), ForeignKey("trips.id"), nullable=False)
    total_cost = Column(Float, nullable=True)  # biaya total untuk kendaraan ini (bensin+tol)
    vehicle_label = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", back_populates="vehicle_groups")
    members = relationship("TripVehicleMember", back_populates="group", cascade="all, delete-orphan")


class TripVehicleMember(Base):
    __tablename__ = "trip_vehicle_members"

    group_id = Column(UUID(as_uuid=False), ForeignKey("trip_vehicle_groups.id"), primary_key=True)
    member_id = Column(UUID(as_uuid=False), ForeignKey("trip_members.id"), primary_key=True)

    group = relationship("TripVehicleGroup", back_populates="members")
    member = relationship("TripMember", back_populates="vehicle_memberships")


class TripHotel(Base):
    __tablename__ = "trip_hotels"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    trip_id = Column(UUID(as_uuid=False), ForeignKey("trips.id"), nullable=False)
    place_id = Column(UUID(as_uuid=False), ForeignKey("places.id"), nullable=False)
    nights = Column(Integer, nullable=False)
    price_per_night = Column(Float, nullable=False)  # pakai Float atau Numeric
    capacity_per_room = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", back_populates="hotels")
    place = relationship("Place")  # asumsi Place sudah ada


class TripActivity(Base):
    __tablename__ = "trip_activities"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    trip_id = Column(UUID(as_uuid=False), ForeignKey("trips.id"), nullable=False)
    place_id = Column(UUID(as_uuid=False), ForeignKey("places.id"), nullable=False)
    day_index = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", back_populates="activities")
    place = relationship("Place")


class TripBudgetSummary(Base):
    __tablename__ = "trip_budget_summary"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    trip_id = Column(UUID(as_uuid=False), ForeignKey("trips.id"), nullable=False)
    total_cost = Column(Float, nullable=False)
    cost_per_member = Column(Float, nullable=False)
    details = Column(Text, nullable=True)  # bisa JSON string atau JSONB, kita pakai Text dulu
    calculated_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", back_populates="budgets")


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

class TripTransport(Base):
    __tablename__ = "trip_transport"

    # Tetap pakai UUID biar konsisten dengan tabel lain
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    trip_id = Column(UUID(as_uuid=False), ForeignKey("trips.id"), nullable=False)
    member_id = Column(UUID(as_uuid=False), ForeignKey("trip_members.id"), nullable=False)
    price = Column(Float, nullable=False)  # atau Numeric(14,2) kalau mau presisi
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relasi opsional (tapi sangat membantu kalau nanti mau ambil data)
    trip = relationship("Trip", back_populates="transport_items")
    member = relationship("TripMember", back_populates="transport")

class PriceReference(Base):
    __tablename__ = "price_reference"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    mode = Column(Enum(TransportMode), nullable=False)
    origin_city = Column(String(255), nullable=False)
    destination_city = Column(String(255), nullable=False)
    estimated_price = Column(Float, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)