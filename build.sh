#!/bin/bash
set -o errexit

# Install Python dependencies
pip install --upgrade pip setuptools wheel
pip install --no-cache-dir --prefer-binary --only-binary=:all: -r requirements.txt || pip install --no-cache-dir -r requirements.txt

# Create instance directory if it doesn't exist
mkdir -p src/instance
mkdir -p src/web/instance

# Initialize database (if needed)
cd src/web
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    try:
        from app import init_sample_data
        init_sample_data()
        print('Sample data initialized')
    except ImportError:
        print('No sample data initialization function found')
"

echo "Build completed successfully!"
