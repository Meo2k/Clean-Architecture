import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Set test environment variables
os.environ.setdefault("ACCESS_TOKEN_KEY", "test_access_token_secret_key_123456789")
os.environ.setdefault("REFRESH_TOKEN_KEY", "test_refresh_token_secret_key_123456789")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/testdb")
os.environ.setdefault("EMAIL_USER", "test@example.com")
os.environ.setdefault("EMAIL_PASSWORD", "test_password")
os.environ.setdefault("ENVIRONMENT", "TESTING")
