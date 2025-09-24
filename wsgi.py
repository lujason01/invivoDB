#!/usr/bin/env python3
"""
WSGI Entry Point for InvivoDB

This is the main WSGI entry point that Render/Gunicorn will use.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the Flask app
from web.app import app

# This is what Gunicorn looks for
if __name__ == "__main__":
    app.run(debug=False)
