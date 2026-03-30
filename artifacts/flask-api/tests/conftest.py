import os

# Must be set before importing the application factory
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["SEED_DATABASE"] = "false"
os.environ["JWT_SECRET"] = "pytest-jwt-secret-key-not-for-production-use"
os.environ["FLASK_ENV"] = "testing"

from app import create_app
import pytest


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def client(app):
    return app.test_client()
