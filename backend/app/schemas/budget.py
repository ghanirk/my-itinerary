from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TripBudgetSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    trip_id: str
    total_cost: float
    cost_per_member: float
    details: Optional[str] = None
    calculated_at: datetime
