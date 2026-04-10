# KIU Portal Frontend - Dockerfile
# Multi-stage build for production optimization

# Stage 1: Build stage
FROM node:18-alpine as builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json .
COPY pnpm-lock.yaml .

# Install dependencies
RUN npm install -g pnpm && \
    pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Build application
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

RUN pnpm build

# Stage 2: Production stage
FROM nginx:alpine

# Install security updates
RUN apk --no-cache add ca-certificates

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built app from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Create non-root user
RUN addgroup -S kiu && adduser -S kiu -G kiu

# Set proper permissions
RUN chown -R kiu:kiu /usr/share/nginx/html && \
    chown -R kiu:kiu /var/cache/nginx && \
    chown -R kiu:kiu /var/log/nginx && \
    chown -R kiu:kiu /etc/nginx/conf.d

# Switch to non-root user
USER kiu

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
