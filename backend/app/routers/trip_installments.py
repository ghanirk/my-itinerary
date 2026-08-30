"""Tahap 6 -- cicilan pembayaran per anggota."""
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Trip, TripMember, MemberRole, TripBudgetSummary, TripInstallment
from app.schemas import TripInstallmentOut, TripInstallmentPay, TripInstallmentAdjust
from app.dependencies import get_current_active_user, get_trip_editor, get_trip_viewer

router = APIRouter(prefix="/trips", tags=["trip-installments"])


def _generate_installments(trip: Trip, months_diff: int, db: Session) -> List[TripInstallment]:
    """Hapus cicilan lama & buat ulang merata per anggota untuk `months_diff` bulan."""
    summary = (
        db.query(TripBudgetSummary)
        .filter(TripBudgetSummary.trip_id == trip.id)
        .order_by(TripBudgetSummary.calculated_at.desc())
        .first()
    )
    if not summary:
        raise HTTPException(400, "Budget not calculated yet")

    members = db.query(TripMember).filter(TripMember.trip_id == trip.id).all()
    if not members:
        raise HTTPException(400, "Trip has no members")

    db.query(TripInstallment).filter(TripInstallment.trip_id == trip.id).delete()

    amount_due_per_month = round(summary.cost_per_member / months_diff, 2)
    new_installments = []
    for member in members:
        for month_idx in range(1, months_diff + 1):
            inst = TripInstallment(
                trip_id=trip.id,
                member_id=member.id,
                month_index=month_idx,
                amount_due=amount_due_per_month,
                amount_paid=0.0,
                paid_at=None,
            )
            db.add(inst)
            new_installments.append(inst)

    db.commit()
    for inst in new_installments:
        db.refresh(inst)
    return new_installments


@router.post("/{trip_id}/installments/generate", response_model=List[TripInstallmentOut])
def generate_installments(trip: Trip = Depends(get_trip_editor), db: Session = Depends(get_db)):
    now = datetime.utcnow()
    target = trip.departure_month_target
    if target < now:
        raise HTTPException(400, "Departure date is in the past")
    months_diff = (target.year - now.year) * 12 + (target.month - now.month)
    if months_diff <= 0:
        months_diff = 1  # minimal 1 bulan untuk cicilan

    return _generate_installments(trip, months_diff, db)


@router.get("/{trip_id}/installments", response_model=List[TripInstallmentOut])
def list_installments(trip: Trip = Depends(get_trip_viewer), db: Session = Depends(get_db)):
    return db.query(TripInstallment).filter(TripInstallment.trip_id == trip.id).all()


@router.put("/{trip_id}/installments/{installment_id}/pay", response_model=TripInstallmentOut)
def pay_installment(
    installment_id: str,
    data: TripInstallmentPay,
    trip: Trip = Depends(get_trip_editor),
    db: Session = Depends(get_db),
):
    installment = db.query(TripInstallment).filter(
        TripInstallment.id == installment_id,
        TripInstallment.trip_id == trip.id,
    ).first()
    if not installment:
        raise HTTPException(404, "Installment not found")

    if data.amount_paid <= 0:
        raise HTTPException(400, "Amount paid must be greater than 0")
    new_paid = installment.amount_paid + data.amount_paid
    if new_paid > installment.amount_due:
        raise HTTPException(400, f"Total paid cannot exceed amount due ({installment.amount_due})")
    installment.amount_paid = new_paid
    installment.paid_at = datetime.utcnow() if new_paid >= installment.amount_due else None

    db.commit()
    db.refresh(installment)
    return installment


@router.post("/{trip_id}/installments/adjust", response_model=List[TripInstallmentOut])
def adjust_installments(
    data: TripInstallmentAdjust,
    trip: Trip = Depends(get_trip_editor),
    db: Session = Depends(get_db),
):
    if data.new_months <= 0:
        raise HTTPException(400, "Number of months must be positive")

    return _generate_installments(trip, data.new_months, db)
