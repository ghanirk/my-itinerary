from pydantic import BaseModel, ConfigDict

from app.schemas.place import PlaceOut


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
