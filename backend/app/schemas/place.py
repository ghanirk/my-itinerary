from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict

from app.models.enums import PlaceCategory, SourceType, PlaceStatus


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
