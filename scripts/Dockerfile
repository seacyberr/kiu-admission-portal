# Multi-stage Dockerfile for KIU Admission Portal
# Production-ready container for Flask API + React Frontend

# ==========================================
# Stage 1: Build Frontend
# ==========================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Install pnpm
RUN npm install -g pnpm

# Copy package files
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY apps/kiu-portal/package.json ./apps/kiu-portal/
COPY lib/api-client-react/package.json ./lib/api-client-react/

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy frontend source
COPY apps/kiu-portal/ ./apps/kiu-portal/
COPY lib/api-client-react/ ./lib/api-client-react/
COPY tsconfig.base.json tsconfig.json ./

# Build frontend
RUN pnpm --filter @workspace/kiu-portal build

# ==========================================
# Stage 2: Python API
# ==========================================
FROM python:3.11-slim AS api

WORKDIR /app/api

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY apps/flask-api/requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy API source
COPY apps/flask-api/ ./

# Create upload directories
RUN mkdir -p uploads/certificates logs

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/api/healthz || exit 1

# Run the application
CMD ["python", "run.py"]

# ==========================================
# Stage 3: Combined Production Image
# ==========================================
FROM python:3.11-slim AS production

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nginx \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY apps/flask-api/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy API source
COPY apps/flask-api/ ./api/
RUN mkdir -p /app/api/uploads/certificates /app/api/logs

# Copy built frontend
COPY --from=frontend-builder /app/apps/kiu-portal/dist /var/www/html

# Copy nginx configuration
COPY docker/nginx.conf /etc/nginx/sites-available/default

# Expose ports
EXPOSE 80 5001

# Start script
COPY docker/start.sh /start.sh
RUN chmod +x /start.sh

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/api/healthz || exit 1

CMD ["/start.sh"]
