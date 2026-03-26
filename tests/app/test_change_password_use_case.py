import pytest

from src.core.result import Return
from src.core.security import hash_password
from src.core.messages import MESSAGES
from src.domain.entities.user import User
from src.domain.value_objects.user import Username, Email, HashedPassword
from src.domain.events.user import PasswordChangedEvent
from src.app.schemas.auth_schema import ChangePasswordCommand
from src.app.use_case.auth.change_password_use_case import ChangePasswordUseCase
from tests.app.test_sign_up_use_case import FakeUnitOfWork


@pytest.mark.asyncio
async def test_change_password_success():
    uow = FakeUnitOfWork()
    hashed_old = hash_password("OldPassword123!")
    user = User.create(
        username=Username("bob_smith"),
        email=Email("bob@example.com"),
        hashed_password=HashedPassword(hashed_old)
    )
    await uow.user_repo.save(user)

    use_case = ChangePasswordUseCase(uow)
    command = ChangePasswordCommand(
        user_id=user.id,
        old_password="OldPassword123!",
        new_password="NewPassword456@"
    )

    result = await use_case.execute(command)

    assert result.is_ok() is True
    assert result.ok_value.message == MESSAGES["AUTH"]["CHANGE_PASSWORD_SUCCESS"]
    assert uow.committed is True

    # Check updated user
    updated_user = (await uow.user_repo.find_by_id(user.id)).ok_value
    assert len(updated_user.events) == 1
    assert isinstance(updated_user.events[0], PasswordChangedEvent)


@pytest.mark.asyncio
async def test_change_password_wrong_old_password():
    uow = FakeUnitOfWork()
    hashed_old = hash_password("OldPassword123!")
    user = User.create(
        username=Username("bob_smith"),
        email=Email("bob@example.com"),
        hashed_password=HashedPassword(hashed_old)
    )
    await uow.user_repo.save(user)

    use_case = ChangePasswordUseCase(uow)
    command = ChangePasswordCommand(
        user_id=user.id,
        old_password="WrongPassword123!",
        new_password="NewPassword456@"
    )

    result = await use_case.execute(command)

    assert result.is_err() is True
    assert result.err_value.code == "invalid_password"


@pytest.mark.asyncio
async def test_change_password_invalid_new_password_format():
    uow = FakeUnitOfWork()
    hashed_old = hash_password("OldPassword123!")
    user = User.create(
        username=Username("bob_smith"),
        email=Email("bob@example.com"),
        hashed_password=HashedPassword(hashed_old)
    )
    await uow.user_repo.save(user)

    use_case = ChangePasswordUseCase(uow)
    command = ChangePasswordCommand(
        user_id=user.id,
        old_password="OldPassword123!",
        new_password="weak"
    )

    result = await use_case.execute(command)

    assert result.is_err() is True
    assert result.err_value.code == "invalid_password_format"


@pytest.mark.asyncio
async def test_change_password_custom_injected_max_attempts():
    uow = FakeUnitOfWork()
    hashed_old = hash_password("OldPassword123!")
    user = User.create(
        username=Username("charlie_test"),
        email=Email("charlie@example.com"),
        hashed_password=HashedPassword(hashed_old)
    )
    await uow.user_repo.save(user)

    # Inject custom max_failed_attempts = 2 directly without monkeypatching settings!
    use_case = ChangePasswordUseCase(uow, max_failed_attempts=2, lock_duration_minutes=15)
    command = ChangePasswordCommand(
        user_id=user.id,
        old_password="WrongPassword123!",
        new_password="NewPassword123!"
    )

    # 1st failure
    res1 = await use_case.execute(command)
    assert res1.is_err() is True
    assert res1.err_value.code == "invalid_password"

    # 2nd failure -> user is locked
    res2 = await use_case.execute(command)
    assert res2.is_err() is True
    assert res2.err_value.code == "invalid_password"

    # 3rd attempt -> user locked error
    res3 = await use_case.execute(command)
    assert res3.is_err() is True
    assert res3.err_value.code == "user_locked"
