#!/usr/bin/env python3
"""
Elastic Beanstalk application entry point.
"""
import sys
import os

# Determine the base directory (where this file is located)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')

# Debug: Print paths (will be in logs)
print(f"BASE_DIR: {BASE_DIR}")
print(f"BACKEND_DIR: {BACKEND_DIR}")
print(f"BACKEND_DIR exists: {os.path.exists(BACKEND_DIR)}")
print(f"sys.path before: {sys.path}")

# Add backend directory to Python path
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Also add base directory
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

print(f"sys.path after: {sys.path}")

# Try to import
try:
    from app import create_app
    print("Successfully imported create_app")
except ImportError as e:
    print(f"Import error: {e}")
    # List files in backend directory for debugging
    if os.path.exists(BACKEND_DIR):
        print(f"Files in backend: {os.listdir(BACKEND_DIR)}")
    raise

# Create the application instance
# EB looks for 'application' variable
try:
    application = create_app()
    print("Successfully created application")
except Exception as e:
    print(f"Error creating app: {e}")
    raise

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    application.run(host="0.0.0.0", port=port)
