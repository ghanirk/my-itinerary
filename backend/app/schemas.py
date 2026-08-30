from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, ConfigDict, Field

from app.models import PlaceCategory, SourceType, PlaceStatus, PlanType, TransportMode, TripStatus, MemberRole



# ---------- Auth / Users ----------

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    email: EmailStr
    is_premium_trial_used: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Places ----------

class PlaceCreate(BaseModel):
    name: str
    category: PlaceCategory
    price_min: int = 0
    price_max: int = 0
    gmaps_url: str
    city: str
    source_type: SourceType = SourceType.manual
    source_url: Optional[str] = None
    photo_url: Optional[str] = None
    opening_hours: Optional[str] = None
    notes: Optional[str] = None
    status: PlaceStatus = PlaceStatus.published


class PlaceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    category: PlaceCategory
    price_min: int
    price_max: int
    gmaps_url: str
    city: str
    source_type: SourceType
    source_url: Optional[str]
    photo_url: Optional[str]
    opening_hours: Optional[str]
    notes: Optional[str]
    status: PlaceStatus
    created_by: str
    created_at: datetime


class PlaceListResponse(BaseModel):
    """Response ter-paginasi untuk GET /places."""
    items: List[PlaceOut]
    total: int  # total item yang cocok dengan filter (sebelum limit/offset)
    limit: int
    offset: int


class PlaceReportCreate(BaseModel):
    reason: str


# ---------- Import via URL Sosmed ----------

class ImportUrlRequest(BaseModel):
    url: str


class ImportPreviewItem(BaseModel):
    """Satu tempat hasil ekstraksi -- video biasa akan punya 1 item, video kompilasi bisa lebih."""
    name: str
    category: PlaceCategory
    price_min: int
    price_max: int
    city: str
    gmaps_url: str  # link PENCARIAN Google Maps auto-generate dari nama+kota -- WAJIB dicek/diganti user sebelum publish
    confidence: str  # "high" atau "low" -- dipakai frontend untuk kasih peringatan ke user
    warning: Optional[str] = None


class ImportPreviewResponse(BaseModel):
    is_compilation: bool
    source_type: SourceType
    source_url: str
    photo_url: Optional[str] = None
    items: List[ImportPreviewItem]


class ImportBulkPlaceItem(BaseModel):
    name: str
    category: PlaceCategory
    price_min: int = 0
    price_max: int = 0
    gmaps_url: str
    city: str
    photo_url: Optional[str] = None
    opening_hours: Optional[str] = None
    notes: Optional[str] = None


class ImportBulkRequest(BaseModel):
    source_type: SourceType
    source_url: str
    items: List[ImportBulkPlaceItem]


class ImportBulkResultItem(BaseModel):
    name: str
    status: str  # "created" | "duplicate" | "error"
    place: Optional[PlaceOut] = None
    detail: Optional[str] = None


class ImportBulkResponse(BaseModel):
    results: List[ImportBulkResultItem]
    created_count: int
    skipped_count: int


# ---------- Plans ----------

class PlanItemCreate(BaseModel):
    place_id: str
    order_index: int = 0


class PlanCreate(BaseModel):
    name: Optional[str] = None
    type: PlanType = PlanType.manual
    budget: Optional[int] = None
    items: List[PlanItemCreate] = []


class PlanItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    place_id: str
    order_index: int
    place: PlaceOut


class PlanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: Optional[str]
    type: PlanType
    budget: Optional[int]
    created_at: datetime
    items: List[PlanItemOut]


class GeneratePlanRequest(BaseModel):
    budget: int
    city: str
    jumlah_tempat: int
    categories: Optional[List[PlaceCategory]] = None



# --- Trip ---
class TripMemberBase(BaseModel):
    user_id: Optional[str] = None  # UUID string
    name: str
    origin_city: str
    role: MemberRole = MemberRole.member

class TripMemberCreate(TripMemberBase):
    pass

class TripMemberOut(TripMemberBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    trip_id: str
    created_at: datetime

class TripTransportCreate(BaseModel):
    price: float

class TripTransportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    trip_id: str
    member_id: str
    price: float
    created_at: datetime

class TripVehicleGroupCreate(BaseModel):
    vehicle_label: str
    member_ids: List[str]  # UUID dari trip_members

class TripVehicleGroupOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    trip_id: str
    vehicle_label: str
    member_ids: List[str]  # kita akan isi dari relasi

class TripHotelCreate(BaseModel):
    place_id: str
    nights: int
    price_per_night: float
    capacity_per_room: int

class TripHotelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    trip_id: str
    place_id: str
    nights: int
    price_per_night: float
    capacity_per_room: int
    place: PlaceOut  # kita reuse PlaceOut

class TripActivityCreate(BaseModel):
    place_id: str
    day_index: int

class TripActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    trip_id: str
    place_id: str
    day_index: int
    place: PlaceOut

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
    # kita bisa tambahkan budget_summary, installments jika diperlukan

# --- Budget & Installment ---
class TripBudgetSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    trip_id: str
    total_cost: float
    cost_per_member: float
    details: Optional[str] = None
    calculated_at: datetime

class TripInstallmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    trip_id: str
    member_id: str
    month_index: int
    amount_due: float
    amount_paid: float
    paid_at: Optional[datetime] = None
    created_at: datetime

class TripInstallmentPay(BaseModel):
    amount_paid: float

class TripInstallmentAdjust(BaseModel):
    new_months: int  # jumlah bulan baru

class TripVehicleGroupUpdateCost(BaseModel):
    total_cost: float

# --- Price Reference (Admin) ---
class PriceReferenceCreate(BaseModel):
    mode: TransportMode
    origin_city: str
    destination_city: str
    estimated_price: float

class PriceReferenceUpdate(BaseModel):
    estimated_price: Optional[float] = None

class PriceReferenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    mode: TransportMode
    origin_city: str
    destination_city: str
    estimated_price: float
    updated_at: datetime


