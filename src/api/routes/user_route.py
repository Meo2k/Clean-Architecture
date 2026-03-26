from fastapi import APIRouter, Depends, Response, status
from fastapi.exceptions import HTTPException

from src.core.settings import settings
from src.core.logger import setup_app_level_logger

from src.api.errors import error_type_handler
from src.api.dependencies.auth_dep import get_current_user
from src.api.dependencies.uow_dep import get_unit_of_work
from src.api.dependencies.cache_dep import get_cache_service

from src.api.schemas.user_schema import UpdateProfileRequest, UserResponse

from src.app.services.unit_of_work_service import UnitOfWork
from src.app.services.cache_service import CacheService
from src.app.use_case.user.update_profile_use_case import UpdateProfileUseCase
from src.app.schemas.user_schema import UpdateProfileCommand


logger = setup_app_level_logger(__name__)


router = APIRouter(prefix="/users", tags=["User"])


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile (with Caching)",
    description="Retrieve user profile with Cache-Aside strategy (Redis / In-memory fallback)."
)
async def get_my_profile(
    response: Response,
    current_user: dict = Depends(get_current_user),
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
    cache_service: CacheService = Depends(get_cache_service),
):
    user_id = str(current_user["id"])
    cache_key = f"user:profile:{user_id}"

    # 1. Cache-Aside: Check cache first
    cached_data = await cache_service.get(cache_key)
    if cached_data:
        response.headers["X-Cache"] = "HIT"
        logger.info(f"Cache HIT for key: {cache_key}")
        return UserResponse(**cached_data)

    # 2. Cache Miss: Query from Database
    response.headers["X-Cache"] = "MISS"
    logger.info(f"Cache MISS for key: {cache_key}. Fetching from DB.")

    async with unit_of_work as uow:
        result = await uow.user_repo.find_by_id(user_id)
        if result.is_err() or not result.ok_value:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        user = result.ok_value

        user_data = UserResponse(
            id=user.id,
            username=user.username.value,
            email=user.email.value,
            phone_number=user.phone_number.value if user.phone_number else None,
            avatar_url=user.avatar_url.value if user.avatar_url else None,
            bio=user.bio,
            status=user.status,
        )

        # 3. Store into Cache for future requests
        await cache_service.set(
            cache_key,
            user_data.model_dump(),
            ttl=settings.CACHE_DEFAULT_TTL
        )

        return user_data


@router.put(
    "/update-profile",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user profile",
    description="Update user profile and invalidate cache"
)
async def update_profile(
    request: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user),
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
    cache_service: CacheService = Depends(get_cache_service),
): 
    # mapping request to command
    command = UpdateProfileCommand(
        user_id=current_user["id"],
        username=request.username,
        phone_number=request.phone_number,
        avatar_url=request.avatar_url,
        bio=request.bio,
    )

    use_case = UpdateProfileUseCase(
        unit_of_work=unit_of_work,
        storage_service=settings.STORAGE_SERVICE,
    )

    result = await use_case.execute(command)

    if result.is_err(): 
        error = result.err_value
        logger.error(f"Failed to update profile for user with id {command.user_id}")
        raise error_type_handler(error, status.HTTP_400_BAD_REQUEST)
    
    # Invalidate cache for this user
    cache_key = f"user:profile:{current_user['id']}"
    await cache_service.delete(cache_key)
    logger.info(f"Invalidated cache for key: {cache_key}")

    # Return success response
    return result.ok_value

