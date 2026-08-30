from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict

from app.models.enums import PlanType, PlaceCategory
from app.schemas.place import PlaceOut


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
