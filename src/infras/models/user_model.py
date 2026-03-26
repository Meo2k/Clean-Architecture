import uuid
import uuid6
from datetime import datetime

from sqlalchemy.orm import Mapped, relationship
from sqlalchemy import String, Boolean, UUID, DateTime, Integer
from sqlalchemy.orm import mapped_column

from src.infras.models.base import Base

class UserModel(Base): 
    """ User model for SQLAlchemy """
    __tablename__ = "users"

    version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, 
        comment="Version of the user record (for optimistic locking)"
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid6.uuid7
    )
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    locked_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    phone_number: Mapped[str] = mapped_column(String(15), nullable=True)
    avatar_url: Mapped[str] = mapped_column(String(255), nullable=True)
    bio: Mapped[str] = mapped_column(String(255), nullable=True)

    # Relationships
    subscriptions: Mapped[list["SubscriptionModel"]] = relationship("SubscriptionModel", back_populates="user")
    orders: Mapped[list["OrderModel"]] = relationship("OrderModel", back_populates="user")

    __mapper_args__ = {
        "version_id_col": version 
    }

    def __repr__(self) -> str: 
        return f"UserModel(id={self.id}, email={self.email}, status={self.status})"