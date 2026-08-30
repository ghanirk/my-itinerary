"""Tahap 3 -- kelompok kendaraan untuk moda transport mobil_pribadi."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    User,
    Trip,
    TripMember,
    MemberRole,
    TransportMode,
    TripVehicleGroup,
    TripVehicleMember,
)
from app.schemas import TripVehicleGroupCreate, TripVehicleGroupOut, TripVehicleGroupUpdateCost
from app.dependencies import get_current_active_user, get_trip_editor, get_trip_viewer

router = APIRouter(prefix="/trips", tags=["trip-vehicles"])


def _serialize_group(group: TripVehicleGroup) -> TripVehicleGroupOut:
    """Bentuk TripVehicleGroupOut dari ORM, termasuk member_ids lewat relasi (bukan raw SQL)."""
    return TripVehicleGroupOut(
        id=group.id,
        trip_id=group.trip_id,
        vehicle_label=group.vehicle_label,
        total_cost=group.total_cost,
        member_ids=[m.member_id for m in group.members],
    )


@router.post("/{trip_id}/vehicle-groups", response_model=TripVehicleGroupOut, status_code=201)
def create_vehicle_group(
    trip_id: str,
    data: TripVehicleGroupCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(404, "Trip not found")
    if trip.transport_mode != TransportMode.mobil_pribadi:
        raise HTTPException(400, "Vehicle groups only for 'mobil_pribadi' mode")
    if trip.owner_id != current_user.id:
        admin = db.query(TripMember).filter(
            TripMember.trip_id == trip_id,
            TripMember.user_id == current_user.id,
            TripMember.role == MemberRole.admin,
        ).first()
        if not admin:
            raise HTTPException(403, "Not authorized")

    group = TripVehicleGroup(trip_id=trip_id, vehicle_label=data.vehicle_label)
    db.add(group)
    db.flush()  # dapatkan group.id sebelum commit

    for member_id in data.member_ids:
        member = db.query(TripMember).filter(
            TripMember.id == member_id,
            TripMember.trip_id == trip_id,
        ).first()
        if not member:
            raise HTTPException(404, f"Member {member_id} not found in trip")
        db.add(TripVehicleMember(group_id=group.id, member_id=member_id))

    db.commit()
    db.refresh(group)
    return _serialize_group(group)


@router.get("/{trip_id}/vehicle-groups", response_model=List[TripVehicleGroupOut])
def list_vehicle_groups(trip: Trip = Depends(get_trip_viewer), db: Session = Depends(get_db)):
    groups = db.query(TripVehicleGroup).filter(TripVehicleGroup.trip_id == trip.id).all()
    return [_serialize_group(g) for g in groups]


@router.put("/{trip_id}/vehicle-groups/{group_id}/cost", response_model=TripVehicleGroupOut)
def update_vehicle_group_cost(
    trip_id: str,
    group_id: str,
    data: TripVehicleGroupUpdateCost,
    trip: Trip = Depends(get_trip_editor),
    db: Session = Depends(get_db),
):
    group = db.query(TripVehicleGroup).filter(
        TripVehicleGroup.id == group_id,
        TripVehicleGroup.trip_id == trip_id,
    ).first()
    if not group:
        raise HTTPException(404, "Vehicle group not found")
    group.total_cost = data.total_cost
    db.commit()
    db.refresh(group)
    return _serialize_group(group)
