#!/bin/bash
set -o errexit

# Install Python dependencies (production only)
pip install --no-cache-dir --prefer-binary -r requirements-prod.txt

# Create instance directory if it doesn't exist
mkdir -p src/instance
mkdir -p src/web/instance

# Initialize database (if needed)
cd src/web
python -c "
from app import app, db, init_sample_data
with app.app_context():
    db.create_all()
    init_sample_data()
"

echo "Build completed successfully!"
