import enum

class OrderStatus(str, enum.Enum):
    """Order payment status."""

    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"

