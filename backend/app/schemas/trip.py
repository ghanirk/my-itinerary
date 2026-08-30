from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict

from app.models.enums import TransportMode, TripStatus
from app.schemas.member import TripMemberOut
from app.schemas.hotel import TripHotelOut
from app.schemas.activity import TripActivityOut


class TripCreate(BaseModel):
    name: str
    destination_city: str
    duration_days: int
    departure_month_target: datetime  # tanggal target
    transport_mode: TransportMode


class TripUpdate(BaseModel):
    name: Optional[str] = None
    destination_city: Optional[str] = None
    duration_days: Optional[int] = None
    departure_month_target: Optional[datetime] = None
    transport_mode: Optional[TransportMode] = None
    status: Optional[TripStatus] = None


class TripOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    owner_id: str
    name: str
    destination_city: str
    duration_days: int
    departure_month_target: datetime
    transport_mode: TransportMode
    status: TripStatus
    created_at: datetime
    updated_at: datetime
    members: Optional[List[TripMemberOut]] = None
    hotels: Optional[List[TripHotelOut]] = None
    activities: Optional[List[TripActivityOut]] = None
    # budget_summary & installments diambil lewat endpoint terpisah
