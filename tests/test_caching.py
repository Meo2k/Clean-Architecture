import pytest
from httpx import AsyncClient, ASGITransport

from main import app
from src.api.dependencies.auth_dep import get_current_user
from src.api.dependencies.uow_dep import get_unit_of_work
from src.api.dependencies.cache_dep import get_cache_service
from src.infras.services.cache_service import InMemoryCacheService
from src.domain.entities.user import User
from src.domain.value_objects.user import Username, Email, HashedPassword
from tests.app.test_sign_up_use_case import FakeUnitOfWork


@pytest.mark.asyncio
async def test_in_memory_cache_service_crud():
    cache = InMemoryCacheService()
    
    # Initially None
    assert await cache.get("key1") is None
    
    # Set and Get
    assert await cache.set("key1", {"data": "test"}, ttl=10) is True
    val = await cache.get("key1")
    assert val == {"data": "test"}

    # Delete
    assert await cache.delete("key1") is True
    assert await cache.get("key1") is None

    # Prefix clear
    await cache.set("user:1", "a")
    await cache.set("user:2", "b")
    await cache.set("order:1", "c")
    cleared = await cache.clear_prefix("user:")
    assert cleared == 2
    assert await cache.get("user:1") is None
    assert await cache.get("order:1") == "c"


@pytest.mark.asyncio
async def test_user_profile_caching_hit_and_miss_and_invalidation():
    # Setup Fake UoW and Cache
    uow = FakeUnitOfWork()
    cache = InMemoryCacheService()

    user = User.create(
        username=Username("cache_test_user"),
        email=Email("cache@example.com"),
        hashed_password=HashedPassword("hash123")
    )
    await uow.user_repo.save(user)

    app.dependency_overrides[get_unit_of_work] = lambda: uow
    app.dependency_overrides[get_cache_service] = lambda: cache
    app.dependency_overrides[get_current_user] = lambda: {
        "id": user.id,
        "email": user.email.value
    }

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. First GET: Cache MISS
            res1 = await client.get("/api/users/me")
            assert res1.status_code == 200
            assert res1.headers.get("x-cache") == "MISS"
            data1 = res1.json()
            assert data1["username"] == "cache_test_user"

            # Verify key exists in cache
            cached_val = await cache.get(f"user:profile:{user.id}")
            assert cached_val is not None
            assert cached_val["username"] == "cache_test_user"

            # 2. Second GET: Cache HIT (Header should be HIT, data same)
            res2 = await client.get("/api/users/me")
            assert res2.status_code == 200
            assert res2.headers.get("x-cache") == "HIT"
            data2 = res2.json()
            assert data2["username"] == "cache_test_user"

            # 3. PUT update-profile: Should invalidate cache
            update_res = await client.put(
                "/api/users/update-profile",
                json={"username": "new_cached_name"}
            )
            assert update_res.status_code == 200
            
            # Cache key must now be deleted (None)
            assert await cache.get(f"user:profile:{user.id}") is None

            # 4. Third GET: Should be Cache MISS again with updated data
            res3 = await client.get("/api/users/me")
            assert res3.status_code == 200
            assert res3.headers.get("x-cache") == "MISS"
            data3 = res3.json()
            assert data3["username"] == "new_cached_name"

    finally:
        app.dependency_overrides.clear()
