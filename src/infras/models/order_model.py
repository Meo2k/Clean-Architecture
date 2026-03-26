import uuid
import uuid6
from datetime import datetime

from sqlalchemy.orm import Mapped, relationship
from sqlalchemy import String, Boolean, Enum, DateTime, Integer, ForeignKey, UUID
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func

from src.infras.models.base import Base
from src.domain.value_objects.order import OrderStatus



class OrderModel(Base): 
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid6.uuid7
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, 
        index=True
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False, default=OrderStatus.PENDING, 
        index=True
    )

    amount: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Amount in VND"
    )

    payment_code: Mapped[str | None] = mapped_column(
        String(255), 
        nullable=True,
        index=True, 
        comment="Payment code for order"
    )

    payment_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), 
        nullable=True,
        comment="Payment time for order"
    )

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
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="orders")

    def __repr__(self) -> str: 
        return f"OrderModel(id={self.id}, user_id={self.user_id}, status={self.status})"