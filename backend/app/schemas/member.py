from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import MemberRole


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
