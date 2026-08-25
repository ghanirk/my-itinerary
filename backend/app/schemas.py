from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, ConfigDict

from app.models import PlaceCategory, SourceType, PlaceStatus, PlanType


# ---------- Auth / Users ----------

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


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
    gmaps_url: Optional[str] = None
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
    gmaps_url: Optional[str]
    city: str
    source_type: SourceType
    source_url: Optional[str]
    photo_url: Optional[str]
    opening_hours: Optional[str]
    notes: Optional[str]
    status: PlaceStatus
    created_by: str
    created_at: datetime


class PlaceReportCreate(BaseModel):
    reason: str


# ---------- Import via URL Sosmed ----------

class ImportUrlRequest(BaseModel):
    url: str


class ImportPreviewResponse(BaseModel):
    """
    Hasil ekstraksi ditampilkan sebagai draft/preview -- BELUM tersimpan ke database.
    Frontend menampilkan ini di form yang bisa diedit user, lalu submit ke POST /places
    (pakai field yang sama, source_type & source_url diisi dari sini) untuk publish.
    """
    name: str
    category: PlaceCategory
    price_min: int
    price_max: int
    city: str
    source_type: SourceType
    source_url: str
    photo_url: Optional[str] = None
    confidence: str  # "high" atau "low" -- dipakai frontend untuk kasih peringatan ke user
    warning: Optional[str] = None


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
