# Use official Python image
FROM python:3.13-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apk update
RUN apk add --no-cache curl build-base libpq-dev tar
RUN ln -sf /bin/tar /bin/gtar

# Install Poetry
ENV POETRY_VERSION=2.1.3
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Set working directory
WORKDIR /app

# Copy only necessary files to install dependencies
COPY backend/pyproject.toml backend/poetry.lock ./

# Install dependencies (no venv, use system python)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy project files
COPY backend .

# Collect static files (optional)
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

WORKDIR /app/backend

# Start server
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]