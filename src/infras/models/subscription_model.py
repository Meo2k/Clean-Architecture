import uuid
import uuid6
from datetime import datetime

from sqlalchemy.orm import Mapped, relationship
from sqlalchemy import String, Boolean, Enum, DateTime, Integer, Float, ForeignKey, UUID
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func

from src.infras.models.base import Base
from src.domain.value_objects.subscription import SubscriptionStatus

class SubscriptionModel(Base): 
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid6.uuid7
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, 
        index=True
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pricing_plans.id", ondelete="RESTRICT"), nullable=False,
        index=True
    )

    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus, values_callable=lambda x: [e.value for e in x]), 
        nullable=False, server_default="active",
        index=True
    )

    current_period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    current_period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="subscriptions")
    plan: Mapped["PricingPlanModel"] = relationship("PricingPlanModel", back_populates="subscriptions")

    def __repr__(self) -> str: 
        return f"SubscriptionModel(id={self.id}, user_id={self.user_id}, plan_id={self.plan_id}, status={self.status})"