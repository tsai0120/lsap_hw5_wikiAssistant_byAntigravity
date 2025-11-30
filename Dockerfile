FROM python:3.13-slim

WORKDIR /app

# Install system dependencies if needed (e.g. for building some python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Configure poetry to not create virtual environments
RUN poetry config virtualenvs.create false

# Copy backend dependencies and install
COPY backend/pyproject.toml backend/poetry.lock /app/backend/
WORKDIR /app/backend
RUN poetry install --no-root --no-interaction --no-ansi

# Copy frontend dependencies and install
COPY frontend/pyproject.toml frontend/poetry.lock /app/frontend/
WORKDIR /app/frontend
RUN poetry install --no-root --no-interaction --no-ansi

# Copy application code
WORKDIR /app
COPY backend /app/backend
COPY frontend /app/frontend
COPY start.sh /app/start.sh

# Make start script executable
RUN chmod +x /app/start.sh

# Expose ports
EXPOSE 8000 8501

# Set entrypoint
CMD ["/app/start.sh"]
