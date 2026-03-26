import uuid
import uuid6
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from src.core.result import ErrorType
from src.infras.repositories.sql_user_repository import SQLUserRepository
from src.infras.repositories.sql_order_repository import SQLOrderRepository
from src.infras.models.user_model import UserModel
from src.infras.models.order_model import OrderModel
from src.domain.entities.user import User
from src.domain.value_objects.user import Username, Email, HashedPassword
from src.domain.entities.order import Order
from src.domain.value_objects.order import OrderStatus


@pytest.mark.asyncio
async def test_sql_user_repository_find_all_success():
    session = AsyncMock()
    user_id = uuid.uuid4()
    mock_model = UserModel(
        id=user_id,
        username="john_doe",
        email="john@example.com",
        password="hashed_password",
        status=True,
        version=1,
        locked_until=None,
        failed_login_attempts=0,
    )

    mock_count_result = MagicMock()
    mock_count_result.scalar_one.return_value = 1

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock_model]
    mock_items_result = MagicMock()
    mock_items_result.scalars.return_value = mock_scalars

    session.execute.side_effect = [mock_count_result, mock_items_result]

    repo = SQLUserRepository(session)
    result = await repo.find_all(page=1, limit=10)

    assert result.is_ok() is True
    users, total = result.ok_value
    assert total == 1
    assert len(users) == 1
    assert users[0].id == str(user_id)
    assert users[0].username.value == "john_doe"
    assert users[0].email.value == "john@example.com"


@pytest.mark.asyncio
async def test_sql_user_repository_find_all_error():
    session = AsyncMock()
    session.execute.side_effect = RuntimeError("Database connection failure")

    repo = SQLUserRepository(session)
    result = await repo.find_all()

    assert result.is_err() is True
    err = result.err_value
    assert err.code == "find_user_error"
    assert err.error_type == ErrorType.INFRA


@pytest.mark.asyncio
async def test_sql_user_repository_delete_success():
    session = AsyncMock()
    user_id_str = str(uuid6.uuid7())
    user = User.create(
        username=Username("to_delete"),
        email=Email("del@example.com"),
        hashed_password=HashedPassword("hash123")
    )
    user.id = user_id_str

    mock_merged_model = MagicMock()
    session.merge.return_value = mock_merged_model

    tracked = []
    repo = SQLUserRepository(session, track_entity=lambda e: tracked.append(e))

    result = await repo.delete(user)

    assert result.is_ok() is True
    assert result.ok_value == user
    session.merge.assert_awaited_once()
    session.delete.assert_awaited_once_with(mock_merged_model)
    assert len(tracked) == 1
    assert tracked[0] == user


@pytest.mark.asyncio
async def test_sql_user_repository_delete_error():
    session = AsyncMock()
    session.merge.side_effect = RuntimeError("DB connection dropped")

    repo = SQLUserRepository(session)
    user = User.create(
        username=Username("to_delete"),
        email=Email("del@example.com"),
        hashed_password=HashedPassword("hash123")
    )

    result = await repo.delete(user)

    assert result.is_err() is True
    assert result.err_value.code == "delete_user_error"
    assert result.err_value.error_type == ErrorType.INFRA
    assert "DB connection dropped" in result.err_value.reason


@pytest.mark.asyncio
async def test_sql_order_repository_save_converts_uuid_and_calls_tracker():
    session = AsyncMock()
    session.add = MagicMock()
    tracked = []

    def mock_track(entity):
        tracked.append(entity)

    repo = SQLOrderRepository(session, track_entity=mock_track)

    order_id_str = str(uuid6.uuid7())
    user_id_str = str(uuid6.uuid7())

    order = Order.create(
        id=order_id_str,
        user_id=user_id_str,
        user_email="test@example.com",
        amount=150000,
        status=OrderStatus.PENDING,
    )

    result = await repo.save(order)

    assert result.is_ok() is True
    saved_order = result.ok_value
    assert saved_order.id == order.id
    assert saved_order.user_id == order.user_id
    assert saved_order.amount == order.amount
    assert saved_order.status == order.status
    assert len(tracked) == 1
    assert tracked[0] == order

    # Verify session.add was called with OrderModel having UUID instances
    session.add.assert_called_once()
    added_model = session.add.call_args[0][0]
    assert isinstance(added_model, OrderModel)
    assert isinstance(added_model.id, uuid.UUID)
    assert added_model.id == uuid.UUID(order_id_str)
    assert isinstance(added_model.user_id, uuid.UUID)
    assert added_model.user_id == uuid.UUID(user_id_str)
    assert added_model.amount == 150000
    assert added_model.status == OrderStatus.PENDING
    session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_sql_order_repository_save_error():
    session = AsyncMock()
    session.add = MagicMock()
    session.flush.side_effect = RuntimeError("Deadlock detected")

    repo = SQLOrderRepository(session)
    order_id_str = str(uuid6.uuid7())
    user_id_str = str(uuid6.uuid7())

    order = Order.create(
        id=order_id_str,
        user_id=user_id_str,
        user_email="test@example.com",
        amount=50000,
    )

    result = await repo.save(order)

    assert result.is_err() is True
    err = result.err_value
    assert err.code == "save_order_error"
    assert isinstance(err.code, str)
    assert err.error_type == ErrorType.INFRA
    assert "Deadlock detected" in err.reason


def test_sql_order_repository_mapping_to_model_and_to_domain():
    order_id_str = str(uuid6.uuid7())
    user_id_str = str(uuid6.uuid7())
    now = datetime.now()

    order = Order(
        id=order_id_str,
        user_id=user_id_str,
        amount=200000,
        status=OrderStatus.PENDING,
        created_at=now,
    )

    # Test _to_model
    model = SQLOrderRepository._to_model(order)
    assert isinstance(model, OrderModel)
    assert model.id == uuid.UUID(order_id_str)
    assert model.user_id == uuid.UUID(user_id_str)
    assert model.amount == 200000
    assert model.status == OrderStatus.PENDING
    assert model.created_at == now

    # Test _to_domain
    domain_order = SQLOrderRepository._to_domain(model)
    assert isinstance(domain_order, Order)
    assert domain_order.id == order_id_str
    assert domain_order.user_id == user_id_str
    assert domain_order.amount == 200000
    assert domain_order.status == OrderStatus.PENDING
    assert domain_order.created_at == now

