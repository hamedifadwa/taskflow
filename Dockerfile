FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Install deps (creates .venv)
COPY pyproject.toml uv.lock ./
RUN uv sync

# Add venv to PATH 👇 (THIS is the key fix)
ENV PATH="/app/.venv/bin:$PATH"

# Copy app
COPY manage.py .
COPY config/ config/
COPY apps/ apps/
COPY static/ static/

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
