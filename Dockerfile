# ==========================================
# STAGE 1: Builder
# ==========================================
FROM python:3.12-slim AS builder

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies into a local directory
RUN pip install --no-cache-dir --user -r requirements.txt

# ==========================================
# STAGE 2: Runtime
# ==========================================
FROM python:3.12-slim

WORKDIR /app

# Python environment variables and PATH for user-installed packages
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

# Copy installed Python packages from the builder stage
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY ./app ./app

EXPOSE 8000

# Start the application (--reload is for development only)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]