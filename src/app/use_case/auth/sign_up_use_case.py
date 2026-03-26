import uuid6

from src.lib.result import Result, Error, Return
from src.lib.logger import setup_app_level_logger
from src.lib.security import hash_password

from src.app.services.unit_of_work_service import UnitOfWork
from src.app.schemas.auth_schema import SignUpCommand, SignUpResult

from src.domain.services.user_registration_service import UserRegistrationDomainService


logger = setup_app_level_logger(__name__)


class SignUpAuthUseCase: 
    """ Use case for creating a new user """
    def __init__(self, unit_of_work: UnitOfWork): 
        self.unit_of_work = unit_of_work

    async def execute(self, command: SignUpCommand) -> Result[SignUpResult, Error]: 
        logger.info(f"Starting to create user with email {command.email}")
        async with self.unit_of_work as uow: 
            user_repo = uow.user_repo
            
            # call domain service to create user
            registration_service = UserRegistrationDomainService(user_repo, hash_password)
            user_result = await registration_service.register_new_user(
                username=command.username,
                email_str=command.email,
                raw_password=command.password
            )
            
            if user_result.is_err():
                logger.error(f"Failed to create user: {user_result.err_value.message}")
                return Return.err(user_result.err_value)
                
            user = user_result.ok_value
            save_result = await user_repo.save(user)

            if save_result.is_err():
                await uow.rollback()
                return save_result

            await uow.commit()
            
            logger.info(f"User with email {command.email} created successfully")
            return Return.ok(SignUpResult(
                message="User created successfully"
            ))
            
    