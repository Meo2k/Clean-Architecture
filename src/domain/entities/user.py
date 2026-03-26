import uuid6

from typing import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from src.domain.errors.exceptions import UserLockedError, InvalidEmailOrPasswordError, InvalidProfileDataError
from src.domain.value_objects.user import Email, HashedPassword, Username, PhoneNumber, AvatarUrl
from src.domain.events.base import Event
from src.domain.events.user import PasswordChangedEvent

@dataclass
class User: 
    """
        Root aggregate representing user aggregate
    """
    id: str
    username: Username
    email: Email      
    password: HashedPassword      
    status: bool
    version: int = 1
    locked_until: datetime | None = None
    failed_login_attempts: int = 0
    
    phone_number: PhoneNumber | None = None
    avatar_url: AvatarUrl | None = None
    bio: str | None = None

    events: list[Event] = field(default_factory=list)

    @classmethod
    def create(cls, username: Username, email: Email, hashed_password: HashedPassword) -> "User":

        return cls(
            id=str(uuid6.uuid7()),
            username=username,
            email=email,
            password=hashed_password,
            status=True,
            locked_until=None,
            failed_login_attempts=0
        )

    def change_password(self, new_hashed_password: HashedPassword): 
        self.password = new_hashed_password
        self.events.append(PasswordChangedEvent(
            user_id=self.id,
            user_email=self.email.value,
            changed_at=datetime.now()
        ))

    def verify_password(self, password_to_check: str, verify_fn: Callable[[str, str], bool], max_attempts: int = 5, lock_duration: timedelta = timedelta(minutes=30)) -> bool:
        """ 
            Compare password and handle lock logic if failed attempts >= max_attempts
            
            Return True if password is correct, False otherwise
            Raise UserLockedError if user is locked
        """

        # check if user is locked  
        if self.locked_until is not None and self.locked_until > datetime.now(): 
            raise UserLockedError("User is locked")
        

        if not verify_fn(password_to_check, self.password.value): 
            self.failed_login_attempts += 1
            if self.failed_login_attempts >= max_attempts: 
                self.locked_until = datetime.now() + lock_duration
            return False

        # reset failed attempts and lock if correct password
        self.failed_login_attempts = 0
        self.locked_until = None
        return True
    
    def update_profile(
        self, 
        username: Username | None = None, 
        phone_number: PhoneNumber | None = None, 
        avatar_url: AvatarUrl | None = None, 
        bio: str | None = None
    ) -> None:
        """ Update user profile fields. Only updates if a value is provided. """
        if username is not None:
            self.username = username
        if phone_number is not None:
            self.phone_number = phone_number
        if avatar_url is not None:
            self.avatar_url = avatar_url
        if bio is not None:
            if len(bio) > 500:
                raise InvalidProfileDataError("Bio must not exceed 500 characters")
            self.bio = bio
