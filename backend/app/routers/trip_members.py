"""Tahap 3 -- anggota trip & transport non-mobil-pribadi per anggota."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Trip, TripMember, MemberRole, TransportMode, TripTransport
from app.schemas import (
    TripMemberCreate,
    TripMemberOut,
    TripTransportCreate,
    TripTransportOut,
)
from app.dependencies import get_current_active_user, get_trip_editor, get_trip_viewer

router = APIRouter(prefix="/trips", tags=["trip-members"])


@router.post("/{trip_id}/members", response_model=TripMemberOut, status_code=201)
def add_member(
    trip_id: str,
    data: TripMemberCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(404, "Trip not found")
    # Otorisasi: hanya owner atau admin yang boleh tambah anggota
    if trip.owner_id != current_user.id:
        admin = db.query(TripMember).filter(
            TripMember.trip_id == trip_id,
            TripMember.user_id == current_user.id,
            TripMember.role == MemberRole.admin,
        ).first()
        if not admin:
            raise HTTPException(403, "Not authorized to add members")

    if data.user_id:
        user_exists = db.query(User).filter(User.id == data.user_id).first()
        if not user_exists:
            raise HTTPException(404, "User not found")
        existing = db.query(TripMember).filter(
            TripMember.trip_id == trip_id,
            TripMember.user_id == data.user_id,
        ).first()
        if existing:
            raise HTTPException(400, "User already a member")
    else:
        if not data.name:
            raise HTTPException(400, "Name required for non-user member")

    member = TripMember(
        trip_id=trip_id,
        user_id=data.user_id,
        name=data.name,
        origin_city=data.origin_city,
        role=data.role,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.get("/{trip_id}/members", response_model=List[TripMemberOut])
def list_members(trip: Trip = Depends(get_trip_viewer), db: Session = Depends(get_db)):
    return db.query(TripMember).filter(TripMember.trip_id == trip.id).all()


@router.delete("/{trip_id}/members/{member_id}", status_code=204)
def remove_member(
    trip_id: str,
    member_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(404, "Trip not found")
    if trip.owner_id != current_user.id:
        admin = db.query(TripMember).filter(
            TripMember.trip_id == trip_id,
            TripMember.user_id == current_user.id,
            TripMember.role == MemberRole.admin,
        ).first()
        if not admin:
            raise HTTPException(403, "Not authorized")

    member = db.query(TripMember).filter(
        TripMember.id == member_id,
        TripMember.trip_id == trip_id,
    ).first()
    if not member:
        raise HTTPException(404, "Member not found")
    db.delete(member)
    db.commit()


# ====================== TRANSPORT (non-mobil) ======================

@router.put("/{trip_id}/members/{member_id}/transport", response_model=TripTransportOut)
def set_transport_price(
    trip_id: str,
    member_id: str,
    data: TripTransportCreate,
    trip: Trip = Depends(get_trip_editor),  # owner atau admin
    db: Session = Depends(get_db),
):
    member = db.query(TripMember).filter(
        TripMember.id == member_id,
        TripMember.trip_id == trip_id,
    ).first()
    if not member:
        raise HTTPException(404, "Member not found")

    if trip.transport_mode == TransportMode.mobil_pribadi:
        raise HTTPException(400, "For 'mobil_pribadi', use vehicle groups instead")

    transport = db.query(TripTransport).filter(
        TripTransport.trip_id == trip_id,
        TripTransport.member_id == member_id,
    ).first()
    if not transport:
        # Buat baru jika belum ada (seharusnya sudah dibuat otomatis saat add member)
        transport = TripTransport(trip_id=trip_id, member_id=member_id, price=0.0)
        db.add(transport)

    transport.price = data.price
    db.commit()
    db.refresh(transport)
    return transport
