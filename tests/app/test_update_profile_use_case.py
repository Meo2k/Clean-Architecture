import pytest

from src.domain.entities.user import User
from src.domain.value_objects.user import Username, Email, HashedPassword
from src.app.schemas.user_schema import UpdateProfileCommand
from src.app.use_case.user.update_profile_use_case import UpdateProfileUseCase
from tests.app.test_sign_up_use_case import FakeUnitOfWork


@pytest.mark.asyncio
async def test_update_profile_success():
    uow = FakeUnitOfWork()
    user = User.create(
        username=Username("initial_nick"),
        email=Email("nick@example.com"),
        hashed_password=HashedPassword("hash123")
    )
    await uow.user_repo.save(user)

    use_case = UpdateProfileUseCase(uow)
    command = UpdateProfileCommand(
        user_id=user.id,
        username="new_nick",
        phone_number="+84912345678",
        avatar_url="https://res.cloudinary.com/demo/image/upload/avatar.jpg",
        bio="Software engineer"
    )

    result = await use_case.execute(command)

    assert result.is_ok() is True
    assert result.ok_value.username == "new_nick"
    assert result.ok_value.phone_number == "+84912345678"
    assert result.ok_value.bio == "Software engineer"
    assert uow.committed is True


@pytest.mark.asyncio
async def test_update_profile_user_not_found():
    uow = FakeUnitOfWork()
    use_case = UpdateProfileUseCase(uow)
    command = UpdateProfileCommand(
        user_id="non_existing_id",
        username="valid_user"
    )

    result = await use_case.execute(command)

    assert result.is_err() is True
    assert result.err_value.code == "user_not_found"


@pytest.mark.asyncio
async def test_update_profile_invalid_data():
    uow = FakeUnitOfWork()
    user = User.create(
        username=Username("initial_nick"),
        email=Email("nick@example.com"),
        hashed_password=HashedPassword("hash123")
    )
    await uow.user_repo.save(user)

    use_case = UpdateProfileUseCase(uow)
    command = UpdateProfileCommand(
        user_id=user.id,
        username="no",  # Invalid: too short (< 3 characters)
    )

    result = await use_case.execute(command)

    assert result.is_err() is True
    assert result.err_value.code == "invalid_profile_data"
