from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import PriceReference, TransportMode
from app.schemas import PriceReferenceCreate, PriceReferenceUpdate, PriceReferenceOut
from app.dependencies import get_current_admin  # kita buat di dependencies.py

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/price-references", response_model=PriceReferenceOut, status_code=201)
def create_price_reference(
    data: PriceReferenceCreate,
    admin: Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    # Cek apakah sudah ada data dengan mode, origin, destination yang sama
    existing = db.query(PriceReference).filter(
        PriceReference.mode == data.mode,
        PriceReference.origin_city == data.origin_city,
        PriceReference.destination_city == data.destination_city
    ).first()
    if existing:
        raise HTTPException(400, "Price reference already exists for this route and mode")
    
    ref = PriceReference(
        mode=data.mode,
        origin_city=data.origin_city,
        destination_city=data.destination_city,
        estimated_price=data.estimated_price,
    )
    db.add(ref)
    db.commit()
    db.refresh(ref)
    return ref


@router.get("/price-references", response_model=List[PriceReferenceOut])
def list_price_references(
    admin: Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    refs = db.query(PriceReference).order_by(PriceReference.mode, PriceReference.origin_city).all()
    return refs


@router.get("/price-references/{ref_id}", response_model=PriceReferenceOut)
def get_price_reference(
    ref_id: str,
    admin: Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    ref = db.query(PriceReference).filter(PriceReference.id == ref_id).first()
    if not ref:
        raise HTTPException(404, "Price reference not found")
    return ref


@router.put("/price-references/{ref_id}", response_model=PriceReferenceOut)
def update_price_reference(
    ref_id: str,
    data: PriceReferenceUpdate,
    admin: Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    ref = db.query(PriceReference).filter(PriceReference.id == ref_id).first()
    if not ref:
        raise HTTPException(404, "Price reference not found")
    
    if data.estimated_price is not None:
        ref.estimated_price = data.estimated_price
    
    db.commit()
    db.refresh(ref)
    return ref


@router.delete("/price-references/{ref_id}", status_code=204)
def delete_price_reference(
    ref_id: str,
    admin: Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    ref = db.query(PriceReference).filter(PriceReference.id == ref_id).first()
    if not ref:
        raise HTTPException(404, "Price reference not found")
    db.delete(ref)
    db.commit()
    return None