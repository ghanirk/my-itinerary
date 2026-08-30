from datetime import datetime

from sqlalchemy import Column, String, Integer, Enum, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.enums import gen_uuid, PlaceCategory, SourceType, PlaceStatus


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
