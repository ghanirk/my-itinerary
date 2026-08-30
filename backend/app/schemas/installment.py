from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


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
