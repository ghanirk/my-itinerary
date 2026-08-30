"""Tahap 2 -- CRUD trip dasar (tanpa anggota/aktivitas)."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Trip, TripStatus, TripMember
from app.schemas import TripCreate, TripUpdate, TripOut
from app.dependencies import get_current_active_user, get_trip_editor, get_trip_viewer

router = APIRouter(prefix="/trips", tags=["trips"])


@router.post("/", response_model=TripOut, status_code=201)
def create_trip(
    data: TripCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    trip = Trip(
        owner_id=current_user.id,
        name=data.name,
        destination_city=data.destination_city,
        duration_days=data.duration_days,
        departure_month_target=data.departure_month_target,
        transport_mode=data.transport_mode,
        status=TripStatus.draft,
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


@router.get("/", response_model=List[TripOut])
def list_trips(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    # User melihat trip yang dia owner atau dia anggota
    owned = db.query(Trip).filter(Trip.owner_id == current_user.id).all()
    member_trips = (
        db.query(Trip).join(TripMember).filter(TripMember.user_id == current_user.id).all()
    )

    # Gabungkan, hilangkan duplikat jika ada (pakai dict by id)
    trips = list({t.id: t for t in owned + member_trips}.values())
    return trips


@router.get("/{trip_id}", response_model=TripOut)
def get_trip(trip: Trip = Depends(get_trip_viewer)):
    return trip


@router.put("/{trip_id}", response_model=TripOut)
def update_trip(
    data: TripUpdate,
    trip: Trip = Depends(get_trip_editor),  # otomatis cek otorisasi owner/admin
    db: Session = Depends(get_db),
):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(trip, field, value)
    db.commit()
    db.refresh(trip)
    return trip


@router.delete("/{trip_id}", status_code=204)
def delete_trip(
    trip_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(404, "Trip not found")

    # Hanya owner yang boleh hapus
    if trip.owner_id != current_user.id:
        raise HTTPException(403, "Only owner can delete trip")

    db.delete(trip)
    db.commit()
    return None
