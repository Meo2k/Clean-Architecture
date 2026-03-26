"""Settings model for admin-configurable defaults."""

from __future__ import annotations

import uuid6
import uuid
from datetime import datetime

from sqlalchemy import DateTime, UUID, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.infras.models.base import Base


class Setting(Base):
    """Admin-configurable settings (e.g., ANTHROPIC_DEFAULT_SONNET_MODEL)."""

    __tablename__ = "settings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid6.uuid7
    )
    key: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
