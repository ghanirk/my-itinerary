from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, ConfigDict, Field

from app.models import PlaceCategory, SourceType, PlaceStatus, PlanType


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
    """
    Hasil ekstraksi ditampilkan sebagai draft/preview -- BELUM tersimpan ke database.
    `items` berisi satu tempat untuk video biasa, atau beberapa tempat sekaligus kalau
    video terdeteksi sebagai kompilasi (mis. "5 kuliner hits di Bandung").
    Frontend menampilkan tiap item di form yang bisa diedit user satu-satu, lalu submit
    ke POST /places/import/bulk (source_type & source_url sama untuk semua item, diambil
    dari sini) untuk publish semuanya sekaligus.
    """
    is_compilation: bool
    source_type: SourceType
    source_url: str
    photo_url: Optional[str] = None
    items: List[ImportPreviewItem]


class ImportBulkPlaceItem(BaseModel):
    """Satu tempat yang sudah dikoreksi user di form preview, siap dipublish."""
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