from datetime import datetime
from src.domain.events.base import Event

class PasswordChangedEvent(Event):
    def __init__(self, user_id: str, user_email: str, changed_at: datetime = None):
        self.user_id = user_id
        self.user_email = user_email
        self.changed_at = changed_at or datetime.now()
