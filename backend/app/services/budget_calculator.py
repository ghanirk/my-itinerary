from sqlalchemy.orm import Session
from typing import Dict, Any
from app.models import Trip, TripMember, TripTransport, TripHotel, TripActivity, TripVehicleGroup, TransportMode, Place, PriceReference
from app.config import settings  # asumsikan ada settings untuk konstanta

# Konstanta untuk estimasi (bisa pindah ke config)
MAKAN_PER_ORANG_PER_HARI = 100000  # Rp 100.000
GRAB_PER_HARI = 50000  # Rp 50.000

def calculate_trip_budget(trip_id: str, db: Session) -> Dict[str, Any]:
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise ValueError("Trip not found")
    
    members = db.query(TripMember).filter(TripMember.trip_id == trip_id).all()
    if not members:
        raise ValueError("Trip has no members")
    
    num_members = len(members)
    
    # 1. Transportasi
    transport_total = 0.0
    if trip.transport_mode != TransportMode.mobil_pribadi:
        # Untuk setiap member, coba ambil dari price_reference, 
        # tapi jika ada TripTransport dengan price > 0, pakai itu.
        for member in members:
            # Cek apakah ada TripTransport yang di-set user
            transport_record = db.query(TripTransport).filter(
                TripTransport.trip_id == trip_id,
                TripTransport.member_id == member.id
            ).first()
            if transport_record and transport_record.price > 0:
                # User sudah mengisi manual, pakai itu
                transport_total += transport_record.price
            else:
                # Cari dari price_reference
                ref = db.query(PriceReference).filter(
                    PriceReference.mode == trip.transport_mode,
                    PriceReference.origin_city == member.origin_city,
                    PriceReference.destination_city == trip.destination_city
                ).first()
                if ref:
                    transport_total += ref.estimated_price
                else:
                    # Tidak ada referensi, beri 0 (atau bisa log warning)
                    transport_total += 0.0
    else:
        # Mobil pribadi: jumlahkan total_cost dari semua group
        groups = db.query(TripVehicleGroup).filter(TripVehicleGroup.trip_id == trip_id).all()
        transport_total = sum(g.total_cost or 0.0 for g in groups)
        # Untuk mobil, transport_total sudah total biaya semua kendaraan.
        # Nanti akan dibagi rata di akhir (cost_per_member = total / num_members)
    # 2. Hotel
    hotels = db.query(TripHotel).filter(TripHotel.trip_id == trip_id).all()
    hotel_total = sum(h.price_per_night * h.nights for h in hotels)
    
    # 3. Aktivitas (tiket masuk)
    activities = db.query(TripActivity).filter(TripActivity.trip_id == trip_id).all()
    place_ids = [a.place_id for a in activities]
    places = db.query(Place).filter(Place.id.in_(place_ids)).all()
    place_price_map = {p.id: p.price_min for p in places}  # ambil price_min sebagai estimasi
    activity_total = sum(place_price_map.get(a.place_id, 0) for a in activities)
    
    # 4. Makan
    makan_total = MAKAN_PER_ORANG_PER_HARI * num_members * trip.duration_days
    
    # 5. Transport lokal (Grab)
    lokal_total = GRAB_PER_HARI * trip.duration_days  # total biaya grab per hari (bukan per orang)? Dokumen: "Estimasi tarif Grab/hari dikalikan jumlah hari" — ini total untuk trip, lalu dibagi rata.
    
    # Total keseluruhan
    total_cost = transport_total + hotel_total + activity_total + makan_total + lokal_total
    cost_per_member = total_cost / num_members
    
    details = {
        "transport": transport_total,
        "hotel": hotel_total,
        "activities": activity_total,
        "makan": makan_total,
        "lokal": lokal_total,
        "num_members": num_members,
        "duration_days": trip.duration_days
    }
    
    return {
        "total_cost": total_cost,
        "cost_per_member": cost_per_member,
        "details": details
    }

def get_transport_price(trip: Trip, member: TripMember, db: Session) -> float:
    """Ambil harga transport dari price_reference berdasarkan mode, origin, destination."""
    # Cek apakah moda mobil? Untuk mobil kita pakai total_cost di vehicle_groups, bukan per anggota.
    if trip.transport_mode == TransportMode.mobil_pribadi:
        return 0.0  # akan dihitung terpisah
    
    ref = db.query(PriceReference).filter(
        PriceReference.mode == trip.transport_mode,
        PriceReference.origin_city == member.origin_city,
        PriceReference.destination_city == trip.destination_city
    ).first()
    if ref:
        return ref.estimated_price
    else:
        # Fallback: kalau tidak ada, return 0 dan kita bisa log warning
        return 0.0