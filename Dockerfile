FROM python:3.14-slim

# Install uv from the official distroless image.
COPY --from=ghcr.io/astral-sh/uv:0.9.25 /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    UV_NO_DEV=1

WORKDIR /app

# Install dependencies first for better layer caching.
COPY pyproject.toml uv.lock* /app/
RUN uv sync --locked --no-cache --no-install-project

# Copy the application code.
COPY . /app

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
