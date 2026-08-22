FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Copy from the cache instead of linking
ENV UV_LINK_MODE=copy

# Install dependencies first for better caching
COPY uv.lock pyproject.toml /app/
RUN uv sync --frozen --no-install-project --no-dev

# Copy the rest of the application
COPY . /app/
RUN uv sync --frozen --no-dev

# Expose port
EXPOSE 8000

# Start server
CMD ["uv", "run", "uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
