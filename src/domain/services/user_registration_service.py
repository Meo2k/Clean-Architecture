from typing import Callable

from src.core.result import Result, Error, Return
from src.core.messages import MESSAGES

from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.domain.value_objects.user import Email, RawPassword, HashedPassword, Username
from src.domain.errors.exceptions import InvalidEmailOrPasswordError, InvalidProfileDataError

class UserRegistrationDomainService:
    def __init__(self, user_repo: UserRepository, password_hasher: Callable[[str], str]):
        self.user_repo = user_repo
        self.password_hasher = password_hasher

    async def register_new_user(self, username: str, email_str: str, raw_password: str) -> Result[User, Error]:
        try:
            username_vo = Username(username)
            email_vo = Email(email_str)
            RawPassword(raw_password) # validate raw password format
        except (InvalidEmailOrPasswordError, InvalidProfileDataError) as e:
            return Return.err(Error(
                code="invalid_user_data",
                message=str(e),
                reason="Invalid email or password format"
            ))

        # check for email duplication (Domain business rule)
        existing_user_result = await self.user_repo.find_by_email(email_vo.value)
        
        if existing_user_result.is_err():
            return Return.err(existing_user_result.err_value)
            
        if existing_user_result.ok_value is not None:
            return Return.err(Error(
                code="user_exists_error",
                message=MESSAGES["AUTH"]["EMAIL_EXISTS"],
                reason=f"Email {email_vo.value} already registered"
            ))

        
        hashed_str = self.password_hasher(raw_password)
        hashed_vo = HashedPassword(hashed_str)

        # Create the User Aggregate Root
        user = User.create(
            username=username_vo,
            email=email_vo,
            hashed_password=hashed_vo
        )

        return Return.ok(user)
