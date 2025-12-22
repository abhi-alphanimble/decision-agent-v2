# Use Python 3.13 as required by your pyproject.toml
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for PostgreSQL adapter)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port AppSail expects (typically 9000)
EXPOSE 9000

# Run database migrations and start the server
# Note: AppSail runs on port 9000 by default inside the container
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 9000"]