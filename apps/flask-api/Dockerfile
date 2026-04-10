# KIU Admission Portal API - Dockerfile
# Multi-stage build for production optimization

# Stage 1: Build stage
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Production stage
FROM python:3.11-slim

# Create non-root user for security
RUN groupadd -r kiu && useradd -r -g kiu kiu

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels

# Install Python packages
RUN pip install --no-cache /wheels/*

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs uploads/certificates && \
    chown -R kiu:kiu /app

# Switch to non-root user
USER kiu

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/api/healthz || exit 1

# Run the application
CMD ["python", "app.py"]
