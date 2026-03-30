#!/usr/bin/env python3
"""Update database with program_choices column for admission applications."""

from app import create_app
from models import db

app = create_app()

with app.app_context():
    # Create all tables (this will add any new columns)
    db.create_all()
    print("Database updated successfully!")
