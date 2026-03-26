import enum

class BillingPeriod(str, enum.Enum):
    """Billing period for subscription."""
    TRIAL = "trial"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"

class Currency(str, enum.Enum):
    """Currency for subscription."""
    VND = "VND"
    USD = "USD"
