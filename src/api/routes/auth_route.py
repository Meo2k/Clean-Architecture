from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi import Response

from config import app_config

from src.lib.logger import setup_app_level_logger

from src.api.routes.error import error_type_handler
from src.api.dependencies.db_dep import get_unit_of_work
from src.api.dependencies.auth_dep import get_current_user
from src.api.schemas.user_schema import UserResponse
from src.api.schemas.auth_schema import (
    SignUpAuthRequest, 
    SignUpAuthResponse, 
    LoginAuthRequest, 
    LoginAuthResponse,
    ChangePasswordAuthRequest,
    ChangePasswordAuthResponse
)

from src.infras.event.get_event_dispatcher import get_event_dispatcher

from src.app.use_case.auth.sign_up_use_case import SignUpAuthUseCase
from src.app.use_case.auth.login_use_case import LoginAuthUseCase
from src.app.use_case.auth.change_password_use_case import ChangePasswordUseCase
from src.app.services.unit_of_work_service import UnitOfWork
from src.app.event.event_dispatcher import EventDispatcher
from src.app.schemas.auth_schema import (
    SignUpCommand, 
    LoginCommand, 
    ChangePasswordCommand
)


logger = setup_app_level_logger(__name__)
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=SignUpAuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Register a new user with email, name, and password"
)
async def register(
    request: SignUpAuthRequest, 
    unit_of_work: UnitOfWork = Depends(get_unit_of_work)
): 
    # mapping
    command = SignUpCommand(
        username=request.username,
        email=request.email,
        password=request.password
    )
    
    logger.info(f"Registering user with email {command.email}")
    
    use_case = SignUpAuthUseCase(unit_of_work)
    result = await use_case.execute(command)
    
    if result.is_err(): 
        error = result.err_value
        logger.error(f"Failed to register user with email {command.email}")
        raise error_type_handler(error, status.HTTP_400_BAD_REQUEST)
    
    # Return success response
    return result.ok_value

@router.post(
    "/login",
    response_model=LoginAuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Login a user",
    description="Login a user with email and password"
)
async def login(
    request: LoginAuthRequest,
    response: Response, 
    unit_of_work: UnitOfWork = Depends(get_unit_of_work)
): 
    # mapping
    command = LoginCommand(
        email=request.email,
        password=request.password
    )
    
    logger.info(f"Logging in user with email {command.email}")
    
    use_case = LoginAuthUseCase(unit_of_work)

    result = await use_case.execute(command)
    
    if result.is_err(): 
        error = result.err_value
        logger.error(f"Failed to login user with email {command.email}")
        if error.code == "user_locked":
            raise error_type_handler(error, status.HTTP_403_FORBIDDEN)
        raise error_type_handler(error, status.HTTP_401_UNAUTHORIZED)

    auth_data = result.ok_value
    response.set_cookie(
        key="refresh_token",
        value=auth_data["refresh_token"],
        httponly=True,
        secure=app_config.IS_HTTPS,
        samesite=app_config.SAME_SITE,
        max_age=app_config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    user_entity = auth_data["user"]
    user_response = UserResponse(
        id=user_entity.id,
        username=user_entity.username,
        email=user_entity.email.value,
        status=user_entity.status,
        phone_number=user_entity.phone_number,
        avatar_url=user_entity.avatar_url,
        bio=user_entity.bio
    )
    
    # Return success response
    return LoginAuthResponse(
        message="Đăng nhập thành công",
        access_token=auth_data["access_token"],
        user=user_response
    )

@router.post(
    "/change-password",
    response_model=ChangePasswordAuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Change user password",
    description="Change password for the currently logged in user"
)
async def change_password(
    request: ChangePasswordAuthRequest,
    current_user: dict = Depends(get_current_user),
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
    event_dispatcher: EventDispatcher = Depends(get_event_dispatcher)
):
    # mapping
    command = ChangePasswordCommand(
        user_id=current_user['id'],
        old_password=request.old_password,
        new_password=request.new_password, 
        logout_other_devices=request.logout_other_devices
    )
    
    logger.info(f"Changing password for user id {command.user_id}")
    
    use_case = ChangePasswordUseCase(unit_of_work, event_dispatcher)
    result = await use_case.execute(command)
    
    if result.is_err():
        error = result.err_value
        logger.error(f"Failed to change password for user id {command.user_id}: {error.message}")
        if error.code == "user_locked":
            raise error_type_handler(error, status.HTTP_403_FORBIDDEN)
        raise error_type_handler(error, status.HTTP_400_BAD_REQUEST)
        
    return result.ok_value

