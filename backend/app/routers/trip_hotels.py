"""Tahap 4 -- hotel per trip."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Trip, TripHotel, Place
from app.schemas import TripHotelCreate, TripHotelOut
from app.dependencies import get_trip_editor, get_trip_viewer

router = APIRouter(prefix="/trips", tags=["trip-hotels"])


@router.post("/{trip_id}/hotels", response_model=TripHotelOut, status_code=201)
def add_hotel(
    trip_id: str,
    data: TripHotelCreate,
    trip: Trip = Depends(get_trip_editor),  # owner/admin
    db: Session = Depends(get_db),
):
    place = db.query(Place).filter(Place.id == data.place_id).first()
    if not place:
        raise HTTPException(404, "Place not found")

    hotel = TripHotel(
        trip_id=trip_id,
        place_id=data.place_id,
        nights=data.nights,
        price_per_night=data.price_per_night,
        capacity_per_room=data.capacity_per_room,
    )
    db.add(hotel)
    db.commit()
    db.refresh(hotel)
    return hotel


@router.get("/{trip_id}/hotels", response_model=List[TripHotelOut])
def list_hotels(trip: Trip = Depends(get_trip_viewer), db: Session = Depends(get_db)):
    return db.query(TripHotel).filter(TripHotel.trip_id == trip.id).all()


@router.delete("/{trip_id}/hotels/{hotel_id}", status_code=204)
def remove_hotel(
    trip_id: str,
    hotel_id: str,
    trip: Trip = Depends(get_trip_editor),
    db: Session = Depends(get_db),
):
    hotel = db.query(TripHotel).filter(
        TripHotel.id == hotel_id,
        TripHotel.trip_id == trip_id,
    ).first()
    if not hotel:
        raise HTTPException(404, "Hotel not found")
    db.delete(hotel)
    db.commit()
