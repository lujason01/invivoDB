#!/usr/bin/env python3
"""
WSGI Entry Point for InvivoDB

This file serves as the entry point for WSGI servers.
Note: With current Procfile setup, this file is not actively used.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the Flask app
try:
    from web.app import app
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback for different path structures
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'web'))
    from app import app

if __name__ == "__main__":
    app.run()
