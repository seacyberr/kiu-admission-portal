"""Prometheus metrics for KIU Portal API."""
import time
from functools import wraps
from flask import request, g
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Request metrics
REQUEST_COUNT = Counter(
    'kiu_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'kiu_http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Database metrics
DB_CONNECTIONS = Gauge(
    'kiu_db_connections_active',
    'Active database connections'
)

DB_QUERY_DURATION = Histogram(
    'kiu_db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation', 'table']
)

# Authentication metrics
AUTH_ATTEMPTS = Counter(
    'kiu_auth_attempts_total',
    'Authentication attempts',
    ['type', 'status']  # type: login/register/verify-otp
)

ACTIVE_USERS = Gauge(
    'kiu_active_users',
    'Number of active users (authenticated in last hour)'
)

# Application metrics
APPLICATIONS_TOTAL = Gauge(
    'kiu_applications_total',
    'Total admission applications',
    ['status']
)

APPLICATIONS_BY_PROGRAM = Gauge(
    'kiu_applications_by_program',
    'Applications per program',
    ['program']
)

# Rate limiting metrics
RATE_LIMIT_HITS = Counter(
    'kiu_rate_limit_hits_total',
    'Rate limit hits',
    ['endpoint', 'user_type']
)

# Business metrics
OPPORTUNITIES_TOTAL = Gauge(
    'kiu_opportunities_total',
    'Total active opportunities',
    ['type']
)

CAREER_PATHS_TOTAL = Gauge(
    'kiu_career_paths_total',
    'Total career paths'
)


def track_request_metrics(f):
    """Decorator to track HTTP request metrics."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            response = f(*args, **kwargs)
            status = response[1] if isinstance(response, tuple) else 200
        except Exception as e:
            status = 500
            raise
        finally:
            duration = time.time() - start_time
            endpoint = request.endpoint or 'unknown'
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=endpoint,
                status=status
            ).inc()
            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(duration)
        
        return response
    return wrapper


def track_auth_metrics(auth_type, status):
    """Track authentication metrics."""
    AUTH_ATTEMPTS.labels(type=auth_type, status=status).inc()


def track_rate_limit(endpoint, user_type='anonymous'):
    """Track rate limit hit."""
    RATE_LIMIT_HITS.labels(endpoint=endpoint, user_type=user_type).inc()


def update_application_metrics():
    """Update application-related gauges."""
    from models import AdmissionApplication, Program
    from sqlalchemy import func
    
    # Total by status
    status_counts = db.session.query(
        AdmissionApplication.status,
        func.count(AdmissionApplication.id)
    ).group_by(AdmissionApplication.status).all()
    
    for status, count in status_counts:
        APPLICATIONS_TOTAL.labels(status=status).set(count)
    
    # By program
    program_counts = db.session.query(
        Program.name,
        func.count(AdmissionApplication.id)
    ).join(AdmissionApplication).group_by(Program.name).all()
    
    for program, count in program_counts:
        APPLICATIONS_BY_PROGRAM.labels(program=program).set(count)


def update_opportunity_metrics():
    """Update opportunity-related gauges."""
    from models import Opportunity
    
    opp_counts = db.session.query(
        Opportunity.type,
        func.count(Opportunity.id)
    ).filter_by(is_active=True).group_by(Opportunity.type).all()
    
    for opp_type, count in opp_counts:
        OPPORTUNITIES_TOTAL.labels(type=opp_type).set(count)


def metrics_endpoint():
    """Expose Prometheus metrics endpoint."""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


def init_metrics(app):
    """Initialize metrics with Flask app."""
    
    @app.route('/metrics')
    def prometheus_metrics():
        return metrics_endpoint()
    
    # Update business metrics periodically
    with app.app_context():
        try:
            update_application_metrics()
            update_opportunity_metrics()
        except Exception:
            pass  # Tables may not exist yet