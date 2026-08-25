import random
from collections import defaultdict
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Plan, PlanItem, Place, User, PlaceStatus, PlanType
from app.schemas import PlanCreate, PlanOut, GeneratePlanRequest
from app.auth import get_current_user

router = APIRouter(prefix="/plans", tags=["plans"])


def _with_items(db: Session, plan_id: str) -> Plan:
    return (
        db.query(Plan)
        .options(joinedload(Plan.items).joinedload(PlanItem.place))
        .filter(Plan.id == plan_id)
        .first()
    )


@router.get("", response_model=List[PlanOut])
def list_my_plans(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(Plan)
        .options(joinedload(Plan.items).joinedload(PlanItem.place))
        .filter(Plan.user_id == current_user.id)
        .order_by(Plan.created_at.desc())
        .all()
    )


@router.post("", response_model=PlanOut, status_code=201)
def create_plan(
    payload: PlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create My Plan (manual) — user sudah memilih sendiri tempat-tempatnya."""
    plan = Plan(
        user_id=current_user.id,
        name=payload.name,
        type=payload.type,
        budget=payload.budget,
    )
    db.add(plan)
    db.flush()  # get plan.id before commit

    for item in payload.items:
        place = db.query(Place).filter(Place.id == item.place_id).first()
        if not place:
            raise HTTPException(status_code=404, detail=f"Tempat {item.place_id} tidak ditemukan.")
        db.add(PlanItem(plan_id=plan.id, place_id=item.place_id, order_index=item.order_index))

    db.commit()
    return _with_items(db, plan.id)


@router.post("/generate", response_model=PlanOut, status_code=201)
def generate_plan(
    payload: GeneratePlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate My Plan (otomatis).
    - Jika categories diisi -> ambil kombinasi dari kategori tsb.
    - Jika tidak -> ambil kombinasi beragam kategori (tidak menumpuk 1 kategori).
    """
    q = db.query(Place).filter(
        Place.status == PlaceStatus.published,
        Place.city.ilike(f"%{payload.city}%"),
        Place.price_min <= payload.budget,
    )
    if payload.categories:
        q = q.filter(Place.category.in_(payload.categories))

    candidates = q.all()
    if not candidates:
        raise HTTPException(status_code=404, detail="Belum ada tempat yang cocok dengan preferensi ini.")

    selected: List[Place] = []

    if payload.categories:
        random.shuffle(candidates)
        selected = candidates[: payload.jumlah_tempat]
    else:
        # Kelompokkan per kategori, ambil bergiliran supaya variatif
        by_category = defaultdict(list)
        for p in candidates:
            by_category[p.category].append(p)
        for places in by_category.values():
            random.shuffle(places)

        categories_cycle = list(by_category.keys())
        i = 0
        while len(selected) < payload.jumlah_tempat and categories_cycle:
            cat = categories_cycle[i % len(categories_cycle)]
            if by_category[cat]:
                selected.append(by_category[cat].pop())
            else:
                categories_cycle.remove(cat)
                continue
            i += 1

    if not selected:
        raise HTTPException(status_code=404, detail="Tidak cukup tempat untuk membuat rencana ini.")

    plan = Plan(user_id=current_user.id, type=PlanType.generated, budget=payload.budget)
    db.add(plan)
    db.flush()

    for idx, place in enumerate(selected):
        db.add(PlanItem(plan_id=plan.id, place_id=place.id, order_index=idx))

    db.commit()
    return _with_items(db, plan.id)


@router.delete("/{plan_id}", status_code=204)
def delete_plan(plan_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.user_id == current_user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan tidak ditemukan.")
    db.delete(plan)
    db.commit()
