from src.app.schemas.user_schema import UpdateProfileCommand, UserResult
from src.app.services.unit_of_work_service import UnitOfWork
from src.lib.result import Result, Error, Return
from src.domain.value_objects.user import Username, PhoneNumber, AvatarUrl
from src.domain.errors.exceptions import InvalidProfileDataError

class UpdateProfileUseCase:
    def __init__(self, unit_of_work: UnitOfWork):
        self.unit_of_work = unit_of_work

    async def execute(self, command: UpdateProfileCommand) -> Result[UserResult, Error]:
        try:
            username_vo = Username(command.username) if command.username is not None else None
            phone_number_vo = PhoneNumber(command.phone_number) if command.phone_number is not None else None
            avatar_url_vo = AvatarUrl(command.avatar_url) if command.avatar_url is not None else None
        except InvalidProfileDataError as e:
            return Return.err(Error(
                code="invalid_profile_data",
                message=str(e),
                reason=str(e)
            ))

        async with self.unit_of_work as uow:
            user_result = await uow.user_repo.find_by_id(command.user_id)
            
            if user_result.is_err():
                return Return.err(user_result.err_value)
            
            user = user_result.ok_value
            if not user:
                return Return.err(Error(
                    code="user_not_found",
                    message="User not found",
                    reason=f"User with id {command.user_id} not found"
                ))

            try:
                user.update_profile(
                    username=username_vo,
                    phone_number=phone_number_vo,
                    avatar_url=avatar_url_vo,
                    bio=command.bio
                )
            except InvalidProfileDataError as e:
                return Return.err(Error(
                    code="invalid_profile_data",
                    message=str(e),
                    reason=str(e)
                ))

            save_result = await uow.user_repo.save(user)
            if save_result.is_err():
                await uow.rollback()
                return Return.err(save_result.err_value)
            
            await uow.commit()

            return Return.ok(UserResult(
                id=user.id,
                username=user.username.value,
                email=user.email.value,
                phone_number=user.phone_number.value if user.phone_number else None,
                avatar_url=user.avatar_url.value if user.avatar_url else None,
                bio=user.bio,
                status=user.status
            ))
    