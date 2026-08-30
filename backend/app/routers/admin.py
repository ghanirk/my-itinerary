"""Tahap 7 -- admin price reference (referensi harga transport per rute)."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PriceReference, User
from app.schemas import PriceReferenceCreate, PriceReferenceUpdate, PriceReferenceOut
from app.dependencies import get_current_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/price-references", response_model=PriceReferenceOut, status_code=201)
def create_price_reference(
    data: PriceReferenceCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    existing = db.query(PriceReference).filter(
        PriceReference.mode == data.mode,
        PriceReference.origin_city == data.origin_city,
        PriceReference.destination_city == data.destination_city,
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
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return db.query(PriceReference).order_by(PriceReference.mode, PriceReference.origin_city).all()


@router.get("/price-references/{ref_id}", response_model=PriceReferenceOut)
def get_price_reference(
    ref_id: str,
    admin: User = Depends(get_current_admin),
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
    admin: User = Depends(get_current_admin),
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
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    ref = db.query(PriceReference).filter(PriceReference.id == ref_id).first()
    if not ref:
        raise HTTPException(404, "Price reference not found")
    db.delete(ref)
    db.commit()
    return None
