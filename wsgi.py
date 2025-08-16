#!/usr/bin/env python3
"""
WSGI Entry Point for InvivoDB

This file serves as the entry point for Gunicorn and other WSGI servers.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the Flask app
from web.app import app

if __name__ == "__main__":
    app.run()
