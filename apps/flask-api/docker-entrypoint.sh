#!/bin/sh
set -e

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Creating database tables..."
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"

echo "Starting Flask application..."
exec flask run --host=0.0.0.0 --port=5001 --reload
