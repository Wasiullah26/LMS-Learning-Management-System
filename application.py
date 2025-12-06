#!/usr/bin/env python3
"""
Elastic Beanstalk application entry point.
"""
import sys
import os

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')

# Add backend directory to Python path - this must happen before any imports
if os.path.exists(BACKEND_DIR) and BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Now import from app (which is in backend/app.py)
# This import must work for the module to load
from app import create_app

# EB looks for 'application' variable - this is what gunicorn will use
application = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    application.run(host="0.0.0.0", port=port)
