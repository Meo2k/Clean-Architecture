import uuid
import uuid6
from datetime import datetime

from sqlalchemy.orm import Mapped
from sqlalchemy import String, Boolean, Enum, DateTime, Integer, UUID
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func

from src.infras.models.base import Base
from src.domain.value_objects.audit_log import AuditLogAction

class AuditLogModel(Base): 
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid6.uuid7
    )
    admin_username: Mapped[str] = mapped_column(String(36), nullable=False)
    action: Mapped[AuditLogAction] = mapped_column(
        Enum(AuditLogAction, values_callable=lambda obj: [e.value for e in obj]), 
        nullable=False, 
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False,
        server_default=func.now()
    )


    def __repr__(self) -> str: 
        return f"AuditLogModel(id={self.id}, admin_username={self.admin_username}, action={self.action})"