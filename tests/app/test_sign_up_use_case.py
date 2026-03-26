import pytest

from src.core.result import Return, Error
from src.core.messages import MESSAGES
from src.app.services.unit_of_work_service import UnitOfWork
from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.order_repository import OrderRepository
from src.domain.entities.user import User
from src.domain.entities.order import Order
from src.app.schemas.auth_schema import SignUpCommand
from src.app.use_case.auth.sign_up_use_case import SignUpAuthUseCase


class FakeUserRepository(UserRepository):
    def __init__(self):
        self.users: dict[str, User] = {}

    async def find_by_id(self, id: str):
        return Return.ok(self.users.get(id))

    async def find_by_email(self, email: str):
        for user in self.users.values():
            if user.email.value == email:
                return Return.ok(user)
        return Return.ok(None)

    async def save(self, entity: User):
        self.users[entity.id] = entity
        return Return.ok(entity)

    async def delete(self, entity: User):
        if entity.id in self.users:
            del self.users[entity.id]
        return Return.ok(entity)

    async def find_all(self, page: int = 1, limit: int = 10):
        items = list(self.users.values())
        return Return.ok((items, len(items)))


class FakeOrderRepository(OrderRepository):
    def __init__(self):
        self.orders: dict[str, Order] = {}

    async def save(self, order: Order):
        self.orders[order.id] = order
        return Return.ok(order)


class FakeUnitOfWork(UnitOfWork):
    def __init__(self):
        self.user_repo = FakeUserRepository()
        self.order_repo = FakeOrderRepository()
        self.committed = False
        self.rolled_back = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.rolled_back = True


@pytest.mark.asyncio
async def test_sign_up_success():
    uow = FakeUnitOfWork()
    use_case = SignUpAuthUseCase(uow)

    command = SignUpCommand(
        username="alice_w",
        email="alice@example.com",
        password="SecurePassword123!"
    )

    result = await use_case.execute(command)

    assert result.is_ok() is True
    assert result.ok_value.message == MESSAGES["AUTH"]["REGISTER_SUCCESS"]
    assert uow.committed is True

    # User should be saved in repo
    saved_user = await uow.user_repo.find_by_email("alice@example.com")
    assert saved_user.ok_value is not None
    assert saved_user.ok_value.username.value == "alice_w"


@pytest.mark.asyncio
async def test_sign_up_duplicate_email():
    uow = FakeUnitOfWork()
    use_case = SignUpAuthUseCase(uow)

    command = SignUpCommand(
        username="alice_w",
        email="alice@example.com",
        password="SecurePassword123!"
    )

    # First sign up
    first_res = await use_case.execute(command)
    assert first_res.is_ok() is True

    # Second sign up with same email
    second_res = await use_case.execute(command)
    assert second_res.is_err() is True
    assert second_res.err_value.code == "user_exists_error"


@pytest.mark.asyncio
async def test_sign_up_invalid_password_format():
    uow = FakeUnitOfWork()
    use_case = SignUpAuthUseCase(uow)

    command = SignUpCommand(
        username="alice_w",
        email="alice@example.com",
        password="weak"
    )

    result = await use_case.execute(command)
    assert result.is_err() is True
    assert result.err_value.code == "invalid_user_data"
