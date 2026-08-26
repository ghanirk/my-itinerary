from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import (
    User, Trip, TripStatus, TripMember, MemberRole, TransportMode,
    TripTransport, TripHotel, TripActivity, Place, TripVehicleGroup
)
from app.schemas import (
    TripCreate, TripUpdate, TripOut,
    TripMemberCreate, TripMemberOut,
    TripTransportCreate, TripTransportOut,
    TripVehicleGroupCreate, TripVehicleGroupOut,
    TripHotelCreate, TripHotelOut,
    TripActivityCreate, TripActivityOut
)
from app.dependencies import get_current_active_user, get_trip_editor

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
    member_trips = db.query(Trip).join(TripMember).filter(
        TripMember.user_id == current_user.id
    ).all()

    # Gabungkan, hilangkan duplikat jika ada (pakai set)
    trips = list({t.id: t for t in owned + member_trips}.values())
    return trips


@router.get("/{trip_id}", response_model=TripOut)
def get_trip(
    trip_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(404, "Trip not found")

    # Cek akses: owner atau anggota
    if trip.owner_id != current_user.id:
        member = db.query(TripMember).filter(
            TripMember.trip_id == trip_id,
            TripMember.user_id == current_user.id
        ).first()
        if not member:
            raise HTTPException(403, "Not authorized to view this trip")

    return trip


@router.put("/{trip_id}", response_model=TripOut)
def update_trip(
    trip_id: str,
    data: TripUpdate,
    trip: Trip = Depends(get_trip_editor),  # otomatis cek otorisasi
    db: Session = Depends(get_db),
):
    # update field yang dikirim
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

@router.post("/{trip_id}/members", response_model=TripMemberOut, status_code=201)
def add_member(
    trip_id: str,
    data: TripMemberCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    # Cek trip ada
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(404, "Trip not found")
    # Otorisasi: hanya owner atau admin yang boleh tambah anggota
    if trip.owner_id != current_user.id:
        admin = db.query(TripMember).filter(
            TripMember.trip_id == trip_id,
            TripMember.user_id == current_user.id,
            TripMember.role == MemberRole.admin
        ).first()
        if not admin:
            raise HTTPException(403, "Not authorized to add members")

    # Cek jika user_id diberikan, pastikan user ada
    if data.user_id:
        user_exists = db.query(User).filter(User.id == data.user_id).first()
        if not user_exists:
            raise HTTPException(404, "User not found")
        # Cek apakah user sudah menjadi anggota trip ini?
        existing = db.query(TripMember).filter(
            TripMember.trip_id == trip_id,
            TripMember.user_id == data.user_id
        ).first()
        if existing:
            raise HTTPException(400, "User already a member")
    else:
        # Jika tidak ada user_id, name harus diisi
        if not data.name:
            raise HTTPException(400, "Name required for non-user member")

    # Buat member
    member = TripMember(
        trip_id=trip_id,
        user_id=data.user_id,
        name=data.name,
        origin_city=data.origin_city,
        role=data.role
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member

@router.get("/{trip_id}/members", response_model=List[TripMemberOut])
def list_members(
    trip_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    # Cek akses: owner atau anggota
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(404, "Trip not found")
    if trip.owner_id != current_user.id:
        member = db.query(TripMember).filter(
            TripMember.trip_id == trip_id,
            TripMember.user_id == current_user.id
        ).first()
        if not member:
            raise HTTPException(403, "Not authorized")
    members = db.query(TripMember).filter(TripMember.trip_id == trip_id).all()
    return members

# ====================== TRANSPORT (non-mobil) ======================

@router.put("/{trip_id}/members/{member_id}/transport", response_model=TripTransportOut)
def set_transport_price(
    trip_id: str,
    member_id: str,
    data: TripTransportCreate,
    trip: Trip = Depends(get_trip_editor),  # owner atau admin
    db: Session = Depends(get_db),
):
    # Pastikan member ada di trip ini
    member = db.query(TripMember).filter(
        TripMember.id == member_id,
        TripMember.trip_id == trip_id
    ).first()
    if not member:
        raise HTTPException(404, "Member not found")

    # Jika moda mobil, sebaiknya tidak pakai endpoint ini, tapi kita biarkan saja
    # atau beri peringatan
    if trip.transport_mode == TransportMode.mobil_pribadi:
        # Boleh diizinkan, tapi lebih baik kasih warning atau tolak
        # Kita tolak agar tidak rancu
        raise HTTPException(400, "For 'mobil_pribadi', use vehicle groups instead")

    transport = db.query(TripTransport).filter(
        TripTransport.trip_id == trip_id,
        TripTransport.member_id == member_id
    ).first()
    if not transport:
        # Buat baru jika belum ada (seharusnya sudah dibuat otomatis saat add member)
        transport = TripTransport(
            trip_id=trip_id,
            member_id=member_id,
            price=0.0
        )
        db.add(transport)

    transport.price = data.price
    db.commit()
    db.refresh(transport)
    return transport

# ====================== HOTELS ======================

@router.post("/{trip_id}/hotels", response_model=TripHotelOut, status_code=201)
def add_hotel(
    trip_id: str,
    data: TripHotelCreate,
    trip: Trip = Depends(get_trip_editor),  # owner/admin
    db: Session = Depends(get_db),
):
    # Pastikan place_id ada dan kategori hotel (optional)
    place = db.query(Place).filter(Place.id == data.place_id).first()
    if not place:
        raise HTTPException(404, "Place not found")
    # Jika mau memaksa kategori hotel, bisa cek:
    # if place.category != PlaceCategory.hotel: raise HTTPException(400, "Place must be hotel")

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
def list_hotels(
    trip_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    # Akses: owner atau anggota
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(404, "Trip not found")
    if trip.owner_id != current_user.id:
        member = db.query(TripMember).filter(
            TripMember.trip_id == trip_id,
            TripMember.user_id == current_user.id
        ).first()
        if not member:
            raise HTTPException(403, "Not authorized")

    hotels = db.query(TripHotel).filter(TripHotel.trip_id == trip_id).all()
    return hotels


@router.delete("/{trip_id}/hotels/{hotel_id}", status_code=204)
def remove_hotel(
    trip_id: str,
    hotel_id: str,
    trip: Trip = Depends(get_trip_editor),
    db: Session = Depends(get_db),
):
    hotel = db.query(TripHotel).filter(
        TripHotel.id == hotel_id,
        TripHotel.trip_id == trip_id
    ).first()
    if not hotel:
        raise HTTPException(404, "Hotel not found")
    db.delete(hotel)
    db.commit()

@router.delete("/{trip_id}/members/{member_id}", status_code=204)
def remove_member(
    trip_id: str,
    member_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    # Otorisasi: owner atau admin
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(404, "Trip not found")
    if trip.owner_id != current_user.id:
        admin = db.query(TripMember).filter(
            TripMember.trip_id == trip_id,
            TripMember.user_id == current_user.id,
            TripMember.role == MemberRole.admin
        ).first()
        if not admin:
            raise HTTPException(403, "Not authorized")

    member = db.query(TripMember).filter(
        TripMember.id == member_id,
        TripMember.trip_id == trip_id
    ).first()
    if not member:
        raise HTTPException(404, "Member not found")
    db.delete(member)
    db.commit()
# ====================== ACTIVITIES ======================

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
def list_activities(
    trip_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(404, "Trip not found")
    if trip.owner_id != current_user.id:
        member = db.query(TripMember).filter(
            TripMember.trip_id == trip_id,
            TripMember.user_id == current_user.id
        ).first()
        if not member:
            raise HTTPException(403, "Not authorized")

    activities = db.query(TripActivity).filter(TripActivity.trip_id == trip_id).all()
    return activities


@router.delete("/{trip_id}/activities/{activity_id}", status_code=204)
def remove_activity(
    trip_id: str,
    activity_id: str,
    trip: Trip = Depends(get_trip_editor),
    db: Session = Depends(get_db),
):
    activity = db.query(TripActivity).filter(
        TripActivity.id == activity_id,
        TripActivity.trip_id == trip_id
    ).first()
    if not activity:
        raise HTTPException(404, "Activity not found")
    db.delete(activity)
    db.commit()

@router.post("/{trip_id}/vehicle-groups", response_model=TripVehicleGroupOut, status_code=201)
def create_vehicle_group(
    trip_id: str,
    data: TripVehicleGroupCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    # Cek trip & otorisasi (owner/admin)
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(404, "Trip not found")
    if trip.transport_mode != TransportMode.mobil_pribadi:
        raise HTTPException(400, "Vehicle groups only for 'mobil_pribadi' mode")
    if trip.owner_id != current_user.id:
        admin = db.query(TripMember).filter(
            TripMember.trip_id == trip_id,
            TripMember.user_id == current_user.id,
            TripMember.role == MemberRole.admin
        ).first()
        if not admin:
            raise HTTPException(403, "Not authorized")

    # Buat group
    group = TripVehicleGroup(
        trip_id=trip_id,
        vehicle_label=data.vehicle_label
    )
    db.add(group)
    db.flush()  # untuk mendapatkan id

    # Tambahkan member ke group melalui tabel asosiasi
    for member_id in data.member_ids:
        # Pastikan member ada di trip ini
        member = db.query(TripMember).filter(
            TripMember.id == member_id,
            TripMember.trip_id == trip_id
        ).first()
        if not member:
            raise HTTPException(404, f"Member {member_id} not found in trip")
        # Tambahkan ke asosiasi
        db.execute(
            "INSERT INTO trip_vehicle_members (group_id, member_id) VALUES (:group_id, :member_id)",
            {"group_id": group.id, "member_id": member_id}
        )
    db.commit()
    db.refresh(group)
    # Kembalikan group dengan member_ids
    # Kita perlu query member_ids untuk response
    return group

@router.get("/{trip_id}/vehicle-groups", response_model=List[TripVehicleGroupOut])
def list_vehicle_groups(
    trip_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    # Akses: owner atau anggota
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(404, "Trip not found")
    if trip.owner_id != current_user.id:
        member = db.query(TripMember).filter(
            TripMember.trip_id == trip_id,
            TripMember.user_id == current_user.id
        ).first()
        if not member:
            raise HTTPException(403, "Not authorized")

    groups = db.query(TripVehicleGroup).filter(TripVehicleGroup.trip_id == trip_id).all()
    # Untuk setiap group, ambil member_ids
    result = []
    for g in groups:
        member_ids = [row[0] for row in db.execute(
            "SELECT member_id FROM trip_vehicle_members WHERE group_id = :gid",
            {"gid": g.id}
        ).fetchall()]
        # Kita perlu TripVehicleGroupOut yang memiliki member_ids
        result.append({
            "id": g.id,
            "trip_id": g.trip_id,
            "vehicle_label": g.vehicle_label,
            "member_ids": member_ids,
            "created_at": g.created_at
        })
    return result