import enum

class AuditLogAction(str, enum.Enum):
    PAYMENT = "payment"
    ORDER = "order"
    SUBSCRIPTION = "subscription"
    