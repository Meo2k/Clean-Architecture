FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy dependency specifications first to leverage Docker layer caching
COPY pyproject.toml uv.lock .python-version /app/

# Install dependencies (frozen to ensure reproducible builds)
RUN uv sync --frozen --no-install-project --no-dev

# Copy application source code
COPY main.py alembic.ini /app/
COPY alembic /app/alembic
COPY src /app/src

# Set PATH to use the virtualenv created by uv
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# Run uvicorn
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
