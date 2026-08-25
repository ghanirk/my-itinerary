from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Place, PlaceReport, User, PlaceCategory, PlaceStatus
from app.schemas import PlaceCreate, PlaceOut, PlaceReportCreate
from app.auth import get_current_user

router = APIRouter(prefix="/places", tags=["places"])


@router.get("", response_model=List[PlaceOut])
def list_places(
    city: Optional[str] = None,
    category: Optional[PlaceCategory] = None,
    budget_min: Optional[int] = Query(None, ge=0),
    budget_max: Optional[int] = Query(None, ge=0),
    db: Session = Depends(get_db),
):
    """
    Filter tempat: by kota, kategori, dan rentang budget.
    Sesuai dokumen: tempat cocok jika rentang harganya overlap dengan budget user.
    """
    q = db.query(Place).filter(Place.status == PlaceStatus.published)

    if city:
        q = q.filter(Place.city.ilike(f"%{city}%"))
    if category:
        q = q.filter(Place.category == category)
    if budget_min is not None:
        q = q.filter(Place.price_max >= budget_min)
    if budget_max is not None:
        q = q.filter(Place.price_min <= budget_max)

    return q.order_by(Place.created_at.desc()).all()


@router.get("/{place_id}", response_model=PlaceOut)
def get_place(place_id: str, db: Session = Depends(get_db)):
    place = db.query(Place).filter(Place.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Tempat tidak ditemukan.")
    return place


@router.post("", response_model=PlaceOut, status_code=201)
def create_place(
    payload: PlaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Deduplication sederhana: cek gmaps_url yang sama persis sebelum simpan
    if payload.gmaps_url:
        dup = db.query(Place).filter(Place.gmaps_url == payload.gmaps_url).first()
        if dup:
            raise HTTPException(
                status_code=409,
                detail=f"Tempat dengan link Google Maps ini sudah ada: '{dup.name}'.",
            )

    place = Place(**payload.model_dump(), created_by=current_user.id)
    db.add(place)
    db.commit()
    db.refresh(place)
    return place


@router.post("/{place_id}/report", status_code=201)
def report_place(
    place_id: str,
    payload: PlaceReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    place = db.query(Place).filter(Place.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Tempat tidak ditemukan.")

    report = PlaceReport(place_id=place_id, user_id=current_user.id, reason=payload.reason)
    db.add(report)
    db.commit()
    return {"message": "Laporan diterima, terima kasih."}
