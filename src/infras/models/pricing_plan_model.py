import uuid
import uuid6

from sqlalchemy.orm import Mapped, relationship
from sqlalchemy import String, Boolean, Enum, DateTime, Integer, Float, UUID
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func
from datetime import datetime

from src.infras.models.base import Base
from src.domain.value_objects.pricing_plan import BillingPeriod, Currency

class PricingPlanModel(Base): 
    __tablename__ = "pricing_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid6.uuid7
    )
    code: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    price: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(
        Enum(Currency, values_callable=lambda x: [e.value for e in x]), 
        nullable=False, server_default="VND", 
        comment="Currency for subscription"
    )
    billing_period: Mapped[str] = mapped_column(
        Enum(BillingPeriod, values_callable=lambda x: [e.value for e in x]), 
        nullable=False, server_default="month", 
        comment="Billing period for subscription"
    )
    interval_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="1",
        comment="Interval count for subscription"
    )

    description: Mapped[str] = mapped_column(String(255), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true", index=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    is_popular: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    subscriptions: Mapped[list["SubscriptionModel"]] = relationship("SubscriptionModel", back_populates="plan")

    def __repr__(self) -> str: 
        return f"PricingPlanModel(id={self.id}, name={self.name}, price={self.price})"