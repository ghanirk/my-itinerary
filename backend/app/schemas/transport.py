from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


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
    total_cost: Optional[float] = None
    member_ids: List[str]  # diisi manual dari relasi TripVehicleMember


class TripVehicleGroupUpdateCost(BaseModel):
    total_cost: float
