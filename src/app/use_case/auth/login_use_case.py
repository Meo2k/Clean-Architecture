from datetime import timedelta
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type

from src.core.result import Result, Error, Return
from src.core.security import create_access_token, create_refresh_token, verify_password
from src.core.messages import MESSAGES

from src.app.services.unit_of_work_service import UnitOfWork
from src.app.schemas.auth_schema import LoginCommand, LoginResult

from src.domain.repositories.user_repository import UserRepository
from src.domain.entities.user import User
from src.domain.errors.exceptions import ConcurrentModificationError, UserLockedError


class LoginAuthUseCase: 
    def __init__(
        self, 
        unit_of_work: UnitOfWork,
        max_failed_attempts: int = 5,
        lock_duration_minutes: int = 30
    ): 
        self.unit_of_work = unit_of_work
        self.max_failed_attempts = max_failed_attempts
        self.lock_duration = timedelta(minutes=lock_duration_minutes)

    # retry for optimistic locking 
    @retry(
        retry=retry_if_exception_type(ConcurrentModificationError),
        stop=stop_after_attempt(3), 
        wait=wait_random_exponential(multiplier=1, max=2),
        reraise=True # if retry 3 times still fail, then raise error
    )
    async def execute(self, command: LoginCommand) -> Result[LoginResult, Error]: 
        async with self.unit_of_work as uow:

            # get user by email
            user = await uow.user_repo.find_by_email(command.email)
          
            if user.is_err():
                return Return.err(user.err_value)

            if user.ok_value is None: 
                return Return.err(Error(
                    code="user_not_found", 
                    message=MESSAGES["AUTH"]["LOGIN_FAILED"], 
                    reason=f"Email {command.email} not found"
                ))

            user_entity = user.ok_value
            try:
                is_valid = user_entity.verify_password(
                    command.password, 
                    verify_fn=verify_password,
                    max_attempts=self.max_failed_attempts, 
                    lock_duration=self.lock_duration
                )
            except UserLockedError as e:
                return Return.err(Error(
                    code="user_locked",
                    message=str(e),
                    reason="User account is temporarily locked due to too many failed attempts"
                ))

            save_result = await uow.user_repo.save(user_entity)
            if save_result.is_err():
                await uow.rollback()
                return save_result

            await uow.commit()
            
        if not is_valid: 
            return Return.err(Error(
                code="invalid_password", 
                message=MESSAGES["AUTH"]["LOGIN_FAILED"], 
                reason="Invalid password"
            ))
            
        # create tokens
        payload = {
            "id": str(user_entity.id),
            "email": user_entity.email.value
        }
        access_token = create_access_token(payload)
        refresh_token = create_refresh_token(payload)

        return Return.ok({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user_entity 
        })
