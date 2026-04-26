import multiprocessing
import os


def _int_env(name, default):
    raw = os.getenv(name, "")
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


# Bind to PORT when provided by host/platform.
bind = f"0.0.0.0:{_int_env('PORT', 5001)}"

# Baseline recommendation: (2 * CPU) + 1, with sane cap/floor.
_workers_default = min(max((multiprocessing.cpu_count() * 2) + 1, 2), 8)
workers = _int_env("WEB_CONCURRENCY", _workers_default)

# Threaded workers help with I/O-heavy API endpoints.
threads = _int_env("GUNICORN_THREADS", 2)
worker_class = "gthread"

# Reliability defaults
timeout = _int_env("GUNICORN_TIMEOUT", 60)
graceful_timeout = _int_env("GUNICORN_GRACEFUL_TIMEOUT", 30)
keepalive = _int_env("GUNICORN_KEEPALIVE", 5)

# Recycle workers periodically to reduce memory bloat risk.
max_requests = _int_env("GUNICORN_MAX_REQUESTS", 1000)
max_requests_jitter = _int_env("GUNICORN_MAX_REQUESTS_JITTER", 100)

# Logging to stdout/stderr for container and PaaS compatibility.
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")

# Helpful process naming in ps/top.
proc_name = "kiu-portal-api"
