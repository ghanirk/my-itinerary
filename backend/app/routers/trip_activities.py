"""Tahap 4 -- aktivitas/itinerary per trip."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Trip, TripActivity, Place
from app.schemas import TripActivityCreate, TripActivityOut
from app.dependencies import get_trip_editor, get_trip_viewer

router = APIRouter(prefix="/trips", tags=["trip-activities"])


@router.post("/{trip_id}/activities", response_model=TripActivityOut, status_code=201)
def add_activity(
    trip_id: str,
    data: TripActivityCreate,
    trip: Trip = Depends(get_trip_editor),
    db: Session = Depends(get_db),
):
    place = db.query(Place).filter(Place.id == data.place_id).first()
    if not place:
        raise HTTPException(404, "Place not found")

    activity = TripActivity(
        trip_id=trip_id,
        place_id=data.place_id,
        day_index=data.day_index,
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


@router.get("/{trip_id}/activities", response_model=List[TripActivityOut])
def list_activities(trip: Trip = Depends(get_trip_viewer), db: Session = Depends(get_db)):
    return db.query(TripActivity).filter(TripActivity.trip_id == trip.id).all()


@router.delete("/{trip_id}/activities/{activity_id}", status_code=204)
def remove_activity(
    trip_id: str,
    activity_id: str,
    trip: Trip = Depends(get_trip_editor),
    db: Session = Depends(get_db),
):
    activity = db.query(TripActivity).filter(
        TripActivity.id == activity_id,
        TripActivity.trip_id == trip_id,
    ).first()
    if not activity:
        raise HTTPException(404, "Activity not found")
    db.delete(activity)
    db.commit()
