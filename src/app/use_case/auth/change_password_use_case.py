from datetime import timedelta

from config import app_config

from src.lib.result import Result, Error, Return
from src.lib.logger import setup_app_level_logger
from src.lib.security import hash_password, verify_password

from src.app.services.unit_of_work_service import UnitOfWork
from src.app.event.event_dispatcher import EventDispatcher
from src.app.schemas.auth_schema import ChangePasswordCommand, ChangePasswordResult

from src.domain.events.user import PasswordChangedEvent
from src.domain.value_objects.user import RawPassword, HashedPassword
from src.domain.errors.exceptions import UserLockedError, InvalidEmailOrPasswordError


logger = setup_app_level_logger(__name__)


class ChangePasswordUseCase:
    def __init__(self, unit_of_work: UnitOfWork, event_dispatcher: EventDispatcher):
        self.unit_of_work = unit_of_work
        self.event_dispatcher = event_dispatcher

    async def execute(self, command: ChangePasswordCommand) -> Result[ChangePasswordResult, Error]:
        """
            Require old password to authenticate before changing password
            After successfully authenticate, change password and save to database
            Dispatch domain event PasswordChangedEvent (send notification email to user)
        """
        async with self.unit_of_work as uow:

            user_result = await uow.user_repo.find_by_id(command.user_id)
            if user_result.is_err():
                return Return.err(user_result.err_value)
                
            if user_result.ok_value is None:
                return Return.err(Error(
                    code="user_not_found",
                    message="User not found",
                ))
                
            user = user_result.ok_value

            # verify old password
            try:
                is_valid = user.verify_password(
                    command.old_password,
                    verify_fn=verify_password,
                    max_attempts=int(app_config.MAX_FAILED_LOGIN_ATTEMPTS),
                    lock_duration=timedelta(minutes=int(app_config.LOCK_DURATION_MINUTES))
                )
            except UserLockedError as e:
                return Return.err(Error(
                    code="user_locked",
                    message=str(e),
                    reason="User account is temporarily locked due to too many failed attempts"
                ))

            if not is_valid:
                # save failed attempts and lock if needed
                save_result = await uow.user_repo.save(user)
                if save_result.is_err():
                    await uow.rollback()
                    return save_result
                    
                await uow.commit()
                
                return Return.err(Error(
                    code="invalid_password",
                    message="Old password is not correct",
                ))
                

            # value object password validation
            try:
                RawPassword(command.new_password)
            except InvalidEmailOrPasswordError as e:
                return Return.err(Error(
                    code="invalid_password_format",
                    message=str(e),
                    reason="New password does not meet complexity requirements"
                ))

            # hash new password and update entity
            hashed_str = hash_password(command.new_password)
            hashed_vo = HashedPassword(hashed_str)
            user.change_password(hashed_vo)
            
            # (optional in future - logout other devices) 


            # save changes
            save_result = await uow.user_repo.save(user)
            if save_result.is_err():
                await uow.rollback()
                return save_result
                
            await uow.commit()
            
        
        # dispatch domain event
        for event in user.events:
            self.event_dispatcher.dispatch(event)
                                
        return Return.ok(ChangePasswordResult(message="Đổi mật khẩu thành công"))
