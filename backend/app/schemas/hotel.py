from pydantic import BaseModel, ConfigDict

from app.schemas.place import PlaceOut


class TripHotelCreate(BaseModel):
    place_id: str
    nights: int
    price_per_night: float
    capacity_per_room: int


class TripHotelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    trip_id: str
    place_id: str
    nights: int
    price_per_night: float
    capacity_per_room: int
    place: PlaceOut  # reuse PlaceOut
