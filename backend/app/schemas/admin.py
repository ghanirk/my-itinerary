from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import TransportMode


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
