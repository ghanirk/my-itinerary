"""Tahap 5 -- kalkulasi & ringkasan budget trip."""
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Trip, TripBudgetSummary
from app.schemas import TripBudgetSummaryOut
from app.services.budget_calculator import calculate_trip_budget
from app.dependencies import get_trip_viewer

router = APIRouter(prefix="/trips", tags=["trip-budget"])


@router.post("/{trip_id}/calculate-budget", response_model=TripBudgetSummaryOut)
def calculate_budget(trip: Trip = Depends(get_trip_viewer), db: Session = Depends(get_db)):
    try:
        result = calculate_trip_budget(trip.id, db)
    except ValueError as e:
        raise HTTPException(400, str(e))

    # Simpan ke summary (hapus yang lama jika ada)
    db.query(TripBudgetSummary).filter(TripBudgetSummary.trip_id == trip.id).delete()
    summary = TripBudgetSummary(
        trip_id=trip.id,
        total_cost=result["total_cost"],
        cost_per_member=result["cost_per_member"],
        details=json.dumps(result["details"]),
    )
    db.add(summary)
    db.commit()
    db.refresh(summary)
    return summary


@router.get("/{trip_id}/budget", response_model=TripBudgetSummaryOut)
def get_budget(trip: Trip = Depends(get_trip_viewer), db: Session = Depends(get_db)):
    summary = db.query(TripBudgetSummary).filter(TripBudgetSummary.trip_id == trip.id).first()
    if not summary:
        raise HTTPException(404, "Budget not calculated yet")
    return summary
