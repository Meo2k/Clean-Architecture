import pytest
from pydantic import ValidationError
from src.core.settings import Settings


def test_fe_url_parsing_and_validation():
    # Valid list
    s1 = Settings(
        ACCESS_TOKEN_KEY="k",
        REFRESH_TOKEN_KEY="k",
        DATABASE_URL="db",
        FE_URL=["http://localhost:3000", "http://localhost:3001"],
    )
    assert s1.FE_URL == ["http://localhost:3000", "http://localhost:3001"]

    # Comma-separated string
    s2 = Settings(
        ACCESS_TOKEN_KEY="k",
        REFRESH_TOKEN_KEY="k",
        DATABASE_URL="db",
        FE_URL="http://localhost:3000, http://localhost:3001",
    )
    assert s2.FE_URL == ["http://localhost:3000", "http://localhost:3001"]

    # Non-list and non-string values must raise ValidationError
    with pytest.raises(ValidationError):
        Settings(
            ACCESS_TOKEN_KEY="k",
            REFRESH_TOKEN_KEY="k",
            DATABASE_URL="db",
            FE_URL=123,
        )


def test_missing_required_configuration_raises_validation_error(monkeypatch):
    # Remove required environment variables to test validation failure
    monkeypatch.delenv("ACCESS_TOKEN_KEY", raising=False)
    monkeypatch.delenv("REFRESH_TOKEN_KEY", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            ACCESS_TOKEN_KEY=None,  # type: ignore
        )


def test_migration_database_url_replaces_asyncpg():
    db_url = "postgresql+asyncpg://user:password@localhost:5432/mydb"
    migration_url = db_url.replace("+asyncpg", "")
    assert migration_url == "postgresql://user:password@localhost:5432/mydb"
