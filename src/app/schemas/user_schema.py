from dataclasses import dataclass

@dataclass
class UserResult: 
    id: str
    username: str
    email: str
    phone_number: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    status: bool = True

@dataclass
class UpdateProfileCommand:
    user_id: str
    username: str | None = None
    phone_number: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
