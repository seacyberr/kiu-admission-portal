# KIU Admission Portal - Deployment & Operations Guide

## Overview

Comprehensive deployment and operations guide for the KIU Admission Portal, covering development, staging, and production environments for Kampala International University.

## Environment Configuration

### Development Environment

#### Local Development Setup
```bash
# Environment variables
export DATABASE_URL=mysql+pymysql://kiu_dev:kiu_dev_password@localhost:3306/kiu_portal_dev
export JWT_SECRET=dev-jwt-secret-change-in-production
export FLASK_ENV=development
export REDIS_URL=redis://localhost:6379/0

# Start services
pnpm dev:api      # Terminal 1: KIU API
pnpm dev:portal    # Terminal 2: KIU Frontend
```

#### Docker Development Setup
```bash
# Using docker-compose.dev.yml
docker compose -f scripts/docker-compose.dev.yml up --build -d
# View logs
docker compose -f scripts/docker-compose.dev.yml logs -f
# Stop services
docker compose -f scripts/docker-compose.dev.yml down
```

### Staging Environment

#### Docker Staging Setup
```bash
# Environment configuration
export FLASK_ENV=staging
export DATABASE_URL=mysql+pymysql://kiu_staging:staging_password@staging-db.kiu.ac.ug:3306/kiu_portal_staging
export JWT_SECRET=staging-jwt-secret-secure
export CORS_ORIGINS=https://staging.kiu.ac.ug

# Deploy staging
docker compose -f scripts/docker-compose.yml --env-file .env.staging build
docker compose -f scripts/docker-compose.yml --env-file .env.staging up -d
```

### Production Environment

#### Docker Production Setup
```bash
# Environment configuration
export FLASK_ENV=production
export DATABASE_URL=mysql+pymysql://kiu_prod:secure_password@prod-db.kiu.ac.ug:3306/kiu_portal
export JWT_SECRET=production-jwt-secret-ultra-secure
export CORS_ORIGINS=https://admissions.kiu.ac.ug,https://portal.kiu.ac.ug

# Deploy production
docker compose -f scripts/docker-compose.yml --env-file .env.prod build
docker compose -f scripts/docker-compose.yml --env-file .env.prod up -d
```

#### Production Infrastructure

**Server Requirements:**
- **CPU**: 4 cores minimum, 8 cores recommended
- **Memory**: 8GB minimum, 16GB recommended
- **Storage**: 100GB SSD minimum, 500GB recommended
- **Network**: 1Gbps dedicated connection
- **Load Balancer**: Nginx with SSL termination

**Database Server:**
- **MySQL**: 8.0 with InnoDB engine
- **Redis**: 7.x for caching and sessions
- **Backups**: Daily automated backups with 30-day retention

## Deployment Strategies

### 1. Blue-Green Deployment

#### Process
```mermaid
graph LR
    A[Current Production] --> B[Deploy New Version]
    B --> C[Test Environment]
    C --> D{Traffic Split: 10% to New}
    D --> E[Monitor Performance]
    E --> F{If Stable: Full Traffic to New}
    F --> G[Decommission Old Version]
```

#### Implementation
```bash
# Deploy new version
docker compose -f scripts/docker-compose.yml --env-file .env.new build
docker compose -f scripts/docker-compose.yml --env-file .env.new up -d

# Health check
curl -f http://new.kiu.ac.ug/health

# Traffic routing (Nginx)
# 10% to new version, 90% to old
```

### 2. Rolling Deployment

#### Process
```mermaid
graph LR
    A[Server 1] --> B[Deploy to Server 2]
    B --> C[Deploy to Server 3]
    C --> D[Deploy to Server 4]
    D --> E[Decommission Server 1]
```

#### Implementation
```bash
# Rolling update script
#!/bin/bash
SERVERS=("server1.kiu.ac.ug" "server2.kiu.ac.ug" "server3.kiu.ac.ug" "server4.kiu.ac.ug")
NEW_VERSION="v1.2.0"

for server in "${SERVERS[@]}"; do
    echo "Deploying to $server..."
    docker compose -f scripts/docker-compose.yml --env-file .env.prod up -d
    sleep 30
done

echo "Rolling deployment completed"
```

### 3. Canary Deployment

#### Process
```mermaid
graph LR
    A[Production] --> B[Deploy Canary Version]
    B --> C{Monitor Canary Metrics}
    C --> D{If Canary Successful: Promote to Production}
```

#### Implementation
```bash
# Canary deployment
docker compose -f scripts/docker-compose.canary.yml up -d

# Monitor canary metrics
curl -f http://canary.kiu.ac.ug/metrics

# Promote if successful
if [[ $(curl -s http://canary.kiu.ac.ug/health) == "healthy" ]]; then
    docker compose -f scripts/docker-compose.yml up -d
fi
```

## Infrastructure as Code (IaC)

### Terraform Configuration

```hcl
# KIU Admission Portal Infrastructure
provider "aws" {
  region = "eu-west-1"
}

# VPC Configuration
resource "aws_vpc" "kiu_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Environment = "production"
    Project = "kiu-admission-portal"
  }
}

# RDS Database
resource "aws_db_instance" "kiu_database" {
  identifier = "kiu-admission-db"
  engine         = "mysql"
  engine_version  = "8.0"
  instance_class = "db.t3.medium"
  allocated_storage = 100
  storage_type    = "gp2"
  vpc_security_group_ids = [aws_security_group.kiu_sg.id]
  db_subnet_group_name   = aws_subnet.kiu_private.id
  
  tags = {
    Environment = "production"
    Project = "kiu-admission-portal"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "kiu_cluster" {
  name = "kiu-admission-cluster"
  instance_type = "FARGATE"
  tags = {
    Environment = "production"
    Project = "kiu-admission-portal"
  }
}

# Application Load Balancer
resource "aws_lb" "kiu_alb" {
  name = "kiu-admission-alb"
  internal = false
  load_balancer_type = "application"
  security_groups = [aws_security_group.kiu_alb_sg.id]
  subnets = [aws_subnet.kiu_public.id]
  
  tags = {
    Environment = "production"
    Project = "kiu-admission-portal"
  }
}
```

### Kubernetes Configuration

```yaml
# KIU Admission Portal - Kubernetes
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kiu-admission-portal
  namespace: kiu-production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: kiu-admission-portal
  template:
    metadata:
      labels:
        app: kiu-admission-portal
    spec:
      containers:
      - name: kiu-api
        image: kiu/admission-api:latest
        ports:
          - containerPort: 5001
        env:
          - name: DATABASE_URL
            valueFrom:
              secretKeyRef:
                name: kiu-db-secret
          - name: JWT_SECRET
            valueFrom:
              secretKeyRef:
                name: kiu-jwt-secret
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
      - name: kiu-frontend
        image: kiu/admission-frontend:latest
        ports:
          - containerPort: 80
        resources:
          requests:
            memory: "256Mi"
            cpu: "125m"
```

## Monitoring & Logging

### Application Monitoring

#### Health Checks
```bash
# API health check
curl -f http://localhost:5001/api/healthz

# Frontend health check
curl -f http://localhost:5173

# Database health check
mysql -h localhost -u kiu_user -p -e "SELECT 1"
```

#### Metrics Collection

```python
# Application metrics endpoint
GET /api/admin/analytics

# Response format
{
  "active_users": 1247,
  "total_applications": 5678,
  "applications_today": 23,
  "server_uptime": "15 days",
  "database_connections": 45,
  "cache_hit_rate": 0.85
}
```

#### Logging Configuration

```python
# Structured logging
import structlog

logger = structlog.get_logger("kiu_admission")

# Log format
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "service": "kiu-api",
  "user_id": 12345,
  "action": "login",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0"
}
```

### Error Tracking

#### Sentry Integration
```python
# Error monitoring
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/project-id",
    integrations=[FlaskIntegration()],
    traces_sample_rate=0.1,
    environment="production"
)
```

#### Custom Error Dashboard
```javascript
// Error tracking
window.KIU_ERROR_TRACKING = {
  trackErrors: true,
  endpoint: '/api/errors/log',
  apiKey: process.env.VITE_ERROR_TRACKING_KEY
};

window.addEventListener('error', (event) => {
  if (window.KIU_ERROR_TRACKING.trackErrors) {
    fetch(window.KIU_ERROR_TRACKING.endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': window.KIU_ERROR_TRACKING.apiKey
      },
      body: JSON.stringify({
        error: event.error.message,
        stack: event.error.stack,
        url: window.location.href,
        userAgent: navigator.userAgent,
        timestamp: new Date().toISOString()
      })
    });
  }
});
```

## Performance Optimization

### Database Performance

#### Query Optimization
```sql
-- Indexes for common queries
CREATE INDEX idx_applications_user_status ON admission_applications(user_id, status);
CREATE INDEX idx_programs_level_faculty ON programs(level, faculty);
CREATE INDEX idx_notifications_user_read ON notifications(user_id, is_read);
```

#### Connection Pooling
```python
# SQLAlchemy configuration
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    pool_recycle=3600
)
```

### Caching Strategy

#### Redis Caching
```python
# Cache configuration
CACHE_CONFIG = {
    'default': {
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_URL': 'redis://localhost:6379/0',
        'CACHE_DEFAULT_TIMEOUT': 300
    }
}

# Cache decorators
from utils.caching import cache_result

@cache_result(timeout=300)
def get_programs():
    # Cached for 5 minutes
    return Program.query.all()
```

### Frontend Optimization

#### Bundle Analysis
```json
// package.json build analysis
{
  "build": {
    "analyze": true,
    "rollupOptions": {
      "output": {
        "manualChunks": {
          "vendor": ["react", "react-dom"],
          "ui": ["@radix-ui/react"]
        }
      }
    }
  }
}
```

#### Performance Budgets
```javascript
// Performance budgets
module.exports = {
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          runtime: 'node_modules'
        }
      }
    }
  },
  performance: {
    budgets: [
      {
        type: 'initial',
        maxEntrypointSize: 512000, // 512KB
        maxAssetSize: 512000
      },
      {
        type: 'javascript',
        maxEntrypointSize: 256000, // 256KB
        maxAssetSize: 256000
      }
    ]
  }
}
```

## Security Operations

### SSL/TLS Management

#### Certificate Management
```bash
# Let's Encrypt automation
certbot --nginx -d admissions.kiu.ac.ug --agree-tos --email admin@kiu.ac.ug

# Certificate renewal (cron)
0 2 * * * /usr/bin/certbot renew --nginx --quiet
```

#### Nginx Configuration
```nginx
# Production SSL configuration
server {
    listen 443 ssl http2;
    server_name admissions.kiu.ac.ug;
    
    ssl_certificate /etc/letsencrypt/live/admissions.kiu.ac.ug/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/admissions.kiu.ac.ug/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Backup & Recovery

### Database Backups

#### Automated Backups
```bash
#!/bin/bash
# Daily backup script
BACKUP_DIR="/backups/kiu-admission-portal"
DATE=$(date +%Y%m%d)
DB_NAME="kiu_portal"

# Create backup
mysqldump -u root -p$DB_ROOT_PASSWORD \
    --single-transaction \
    --routines \
    --triggers \
    $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Upload to cloud storage
aws s3 cp $BACKUP_DIR/backup_$DATE.sql.gz s3://kiu-backups/database/backup_$DATE.sql.gz

# Clean old backups (30 days)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
```

#### Point-in-Time Recovery

```bash
# Binary logs for point-in-time recovery
mysqlbinlog --start-date="2024-01-15 00:00:00" \
    --stop-date="2024-01-15 23:59:59" \
    /var/log/mysql/mysql-bin.*

# Restore from backup
mysql -u root -p$DB_ROOT_PASSWORD \
    < $BACKUP_DIR/backup_20240115.sql
```

### Disaster Recovery

#### Recovery Procedures
```bash
# Disaster recovery checklist
1. Assess damage and scope
2. Restore from latest clean backup
3. Verify data integrity
4. Test all system functionality
5. Monitor for post-recovery issues
6. Document incident and lessons learned

# Recovery script
#!/bin/bash
echo "Starting KIU Admission Portal disaster recovery..."

# Stop all services
docker compose -f scripts/docker-compose.yml down

# Restore database
mysql -u root -p$DB_ROOT_PASSWORD \
    kiu_portal < /backups/latest_clean.sql

# Restart services
docker compose -f scripts/docker-compose.yml up -d

echo "Disaster recovery completed"
```

## Scaling Operations

### Horizontal Scaling

#### Database Scaling
```yaml
# Read replica configuration
version: '3.8'
services:
  mysql-master:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: $DB_ROOT_PASSWORD
      MYSQL_DATABASE: kiu_portal
    volumes:
      - mysql_data:/var/lib/mysql
  
  mysql-replica-1:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: $DB_ROOT_PASSWORD
      MYSQL_DATABASE: kiu_portal
      MYSQL_REPLICA_SOURCE: mysql-master
    volumes:
      - mysql_replica_data:/var/lib/mysql
```

#### Application Scaling
```yaml
# Multi-instance deployment
version: '3.8'
services:
  kiu-api-1:
    image: kiu/admission-api:latest
    ports:
      - "5001:5001"
    environment:
      INSTANCE_ID: "1"
  
  kiu-api-2:
    image: kiu/admission-api:latest
    ports:
      - "5002:5001"
    environment:
      INSTANCE_ID: "2"
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d
    depends_on:
      - kiu-api-1
      - kiu-api-2
```

### Load Balancing

#### Nginx Load Balancer
```nginx
upstream kiu_api_backend {
    server kiu-api-1:5001 weight=3 max_fails=3 fail_timeout=30s;
    server kiu-api-2:5001 weight=3 max_fails=3 fail_timeout=30s;
    server kiu-api-3:5001 weight=2 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name admissions.kiu.ac.ug;
    
    location /api/ {
        proxy_pass http://kiu_api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        health_check;
    }
}
```

## Maintenance Operations

### Scheduled Maintenance

#### Maintenance Windows
```bash
#!/bin/bash
# Maintenance mode activation
echo "Activating KIU Admission Portal maintenance mode..."

# Update maintenance page
sed -i 's/MAINTENANCE_MODE = false/MAINTENANCE_MODE = true/' apps/flask-api/config.py

# Restart services with maintenance flag
docker compose -f scripts/docker-compose.yml restart

echo "Maintenance mode activated"
```

#### Database Maintenance
```sql
-- Maintenance operations
-- Optimize tables
OPTIMIZE TABLE admission_applications;
OPTIMIZE TABLE users;
OPTIMIZE TABLE programs;

-- Update statistics
ANALYZE TABLE admission_applications;
ANALYZE TABLE users;
ANALYZE TABLE programs;

-- Clean up old data
DELETE FROM notifications WHERE created_at < DATE_SUB(NOW(), INTERVAL 90 DAY);
DELETE FROM audit_logs WHERE created_at < DATE_SUB(NOW(), INTERVAL 365 DAY);
```

## Troubleshooting

### Common Issues

**Database Issues**
```bash
# Check connections: mysql -h localhost -u kiu_user -p -e "SHOW PROCESSLIST"
# Check slow queries: mysql -h localhost -u kiu_user -p -e "SELECT * FROM mysql.slow_log ORDER BY start_time DESC LIMIT 10"
# Check locks: mysql -h localhost -u kiu_user -p -e "SHOW ENGINE INNODB STATUS"
```

**Application Issues**
```bash
# Check logs: docker compose -f scripts/docker-compose.yml logs kiu-api
# Check resources: docker stats
# Restart service: docker compose -f scripts/docker-compose.yml restart kiu-api
# Scale: docker compose -f scripts/docker-compose.yml up -d --scale kiu-api=3
```

**Network Issues**
```bash
# Check connectivity: telnet localhost 5001
# Check SSL: openssl s_client -connect admissions.kiu.ac.ug:443 -servername admissions.kiu.ac.ug
```

## Security Operations

### Security Auditing
```bash
# Security audit
nmap -sS -sV admissions.kiu.ac.ug -p 80,443,5001
curl -I https://admissions.kiu.ac.ug
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec tr image:admissions.kiu.ac.ug:latest
```

### Incident Response
```bash
# Security incident response
#!/bin/bash
SEVERITY_LEVEL=$1
INCIDENT_TYPE="security_breach"
AFFECTED_SYSTEMS="api,database,frontend"

echo "Security incident detected - Severity: $SEVERITY_LEVEL"
docker compose -f scripts/docker-compose.yml stop
echo "Assessing impact..."
echo "Notifying security team..."
echo "Implementing recovery..."
echo "Documenting incident..."
```

---

*Last Updated: January 2024*
