from datetime import datetime

from sqlalchemy import Column, String, Integer, Enum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.enums import gen_uuid, PlanType


class Plan(Base):
    __tablename__ = "plans"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=True)
    type = Column(Enum(PlanType), default=PlanType.manual, nullable=False)
    budget = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="plans")
    items = relationship(
        "PlanItem", back_populates="plan", cascade="all, delete-orphan", order_by="PlanItem.order_index"
    )


class PlanItem(Base):
    __tablename__ = "plan_items"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    plan_id = Column(UUID(as_uuid=False), ForeignKey("plans.id"), nullable=False)
    place_id = Column(UUID(as_uuid=False), ForeignKey("places.id"), nullable=False)
    order_index = Column(Integer, default=0)

    plan = relationship("Plan", back_populates="items")
    place = relationship("Place")
