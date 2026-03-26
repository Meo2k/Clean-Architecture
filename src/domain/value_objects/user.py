
import re
from dataclasses import dataclass
from src.domain.errors.exceptions import InvalidEmailOrPasswordError, InvalidProfileDataError

EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

@dataclass(frozen=True) 
class Email:
    value: str

    def __post_init__(self):
        if not re.match(EMAIL_REGEX, self.value):
            raise InvalidEmailOrPasswordError("Invalid email format")

@dataclass(frozen=True)
class RawPassword:
    value: str

    def __post_init__(self):
        # check length
        if len(self.value) < 8:
            raise InvalidEmailOrPasswordError("Password must be at least 8 characters long")
        
        # check uppercase
        if not re.search(r"[A-Z]", self.value):
            raise InvalidEmailOrPasswordError("Password must contain at least one uppercase letter")
            
        # check lowercase
        if not re.search(r"[a-z]", self.value):
            raise InvalidEmailOrPasswordError("Password must contain at least one lowercase letter")
            
        # check digit
        if not re.search(r"\d", self.value):
            raise InvalidEmailOrPasswordError("Password must contain at least one digit")
            
        # check special character
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", self.value):
            raise InvalidEmailOrPasswordError("Password must contain at least one special character")

@dataclass(frozen=True)
class HashedPassword:
    value: str

@dataclass(frozen=True)
class Username:
    value: str

    def __post_init__(self):
        if not re.match(r"^[a-zA-Z0-9_]{3,30}$", self.value):
            raise InvalidProfileDataError("Username must be between 3 and 30 characters and contain only letters, numbers, and underscores")

@dataclass(frozen=True)
class PhoneNumber:
    value: str

    def __post_init__(self):
        if not re.match(r"^\+?[0-9]\d{1,14}$", self.value):
            raise InvalidProfileDataError("Invalid phone number format")

IMAGE_URL_REGEX = r"^https?://[^\s/$.?#].[^\s]*\.(jpg|jpeg|png|webp|gif|svg)(\?.*)?$"

@dataclass(frozen=True)
class AvatarUrl:
    value: str

    def __post_init__(self):
        if len(self.value) > 2048:
            raise InvalidProfileDataError("Avatar URL must not exceed 2048 characters")
        if not re.match(IMAGE_URL_REGEX, self.value, re.IGNORECASE):
            raise InvalidProfileDataError("Avatar URL must be a valid image HTTP/HTTPS URL")
