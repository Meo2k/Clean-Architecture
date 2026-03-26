from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from src.lib.logger import setup_app_level_logger

from src.api.routes.error import error_type_handler
from src.api.dependencies.auth_dep import get_current_user
from src.api.dependencies.db_dep import get_unit_of_work

from src.api.schemas.user_schema import UpdateProfileRequest

from src.app.services.unit_of_work_service import UnitOfWork
from src.app.use_case.user.update_profile_use_case import UpdateProfileUseCase
from src.app.schemas.user_schema import UpdateProfileCommand


logger = setup_app_level_logger(__name__)


router = APIRouter(prefix="/users", tags=["User"])

@router.get(
    "/update-profile",
    status_code=status.HTTP_200_OK,
    summary="Update user profile",
    description="Update user profile"
)
async def update_profile(
    request: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user),
    unit_of_work: UnitOfWork = Depends(get_unit_of_work)
): 
    # mapping request to command
    command = UpdateProfileCommand(
        user_id=current_user["id"],
        username=request.username,
        phone_number=request.phone_number,
        avatar_url=request.avatar_url,
        bio=request.bio,
    )

    use_case = UpdateProfileUseCase(unit_of_work)

    result = await use_case.execute(command)

    if result.is_err(): 
        error = result.err_value
        logger.error(f"Failed to update profile for user with email {command.email}")
        raise error_type_handler(error, status.HTTP_400_BAD_REQUEST)
    
    # Return success response
    return result.ok_value

    return result.ok_value
    

    

    
    
