from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.models import User, Trip, TripMember, MemberRole
from app.auth import get_current_user  # pastikan di auth.py ada fungsi ini


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    # Bisa tambahkan pengecekan aktif jika diperlukan
    return current_user


def get_current_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def get_trip_editor(
    trip_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Trip:
    """
    Dependency untuk mengecek apakah user boleh mengedit trip.
    - Owner (trips.owner_id == current_user.id)
    - Atau anggota dengan role 'admin'
    """
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    # Cek apakah user adalah owner
    if trip.owner_id == current_user.id:
        return trip

    # Cek apakah user adalah anggota dengan role admin
    member = db.query(TripMember).filter(
        TripMember.trip_id == trip_id,
        TripMember.user_id == current_user.id,
        TripMember.role == MemberRole.admin
    ).first()
    if member:
        return trip

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authorized to edit this trip",
    )


def get_trip_viewer(
    trip_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Trip:
    """
    Dependency untuk mengecek apakah user boleh melihat trip (owner ATAU anggota apa pun).
    Dipakai di banyak endpoint GET yang sebelumnya menduplikasi pengecekan ini manual.
    """
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    if trip.owner_id == current_user.id:
        return trip

    member = db.query(TripMember).filter(
        TripMember.trip_id == trip_id,
        TripMember.user_id == current_user.id,
    ).first()
    if member:
        return trip

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")