import pytest
from httpx import AsyncClient, ASGITransport

from main import app
from src.core.settings import settings
from src.api.dependencies.auth_dep import get_current_user
from src.api.dependencies.uow_dep import get_unit_of_work
from src.domain.entities.user import User
from src.domain.value_objects.user import Username, Email, HashedPassword
from tests.app.test_sign_up_use_case import FakeUnitOfWork


@pytest.mark.asyncio
async def test_health_check_endpoint():
    assert app.title == settings.SYS_NAME
    assert app.version == settings.VERSION

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == settings.SYS_NAME
        assert data["version"] == settings.VERSION


@pytest.mark.asyncio
async def test_update_profile_route_put_method():
    uow = FakeUnitOfWork()
    user = User.create(
        username=Username("initial_nick"),
        email=Email("nick@example.com"),
        hashed_password=HashedPassword("hash123")
    )
    await uow.user_repo.save(user)

    app.dependency_overrides[get_unit_of_work] = lambda: uow
    app.dependency_overrides[get_current_user] = lambda: {
        "id": user.id,
        "email": "nick@example.com"
    }

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            payload = {
                "username": "updated_nick",
                "phone_number": "+84912345678",
                "bio": "Updated bio text"
            }
            # Verify PUT works
            response = await client.put("/api/users/update-profile", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["username"] == "updated_nick"
            assert data["bio"] == "Updated bio text"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_order_route_uses_id_key():
    uow = FakeUnitOfWork()

    # current_user strictly uses key 'id'
    app.dependency_overrides[get_unit_of_work] = lambda: uow
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "user-uuid-1234",
        "email": "buyer@example.com"
    }

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            payload = {
                "amount": 250000
            }
            response = await client.post("/api/order/", json=payload)
            assert response.status_code == 201
            data = response.json()
            assert data["message"] == "Order created successfully"
            assert len(uow.order_repo.orders) == 1
            saved_order = list(uow.order_repo.orders.values())[0]
            assert saved_order.user_id == "user-uuid-1234"
            assert saved_order.amount == 250000
    finally:
        app.dependency_overrides.clear()
