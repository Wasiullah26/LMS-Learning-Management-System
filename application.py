#!/usr/bin/env python3
"""
Elastic Beanstalk application entry point.
"""
import sys
import os

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')

# Add backend directory to Python path
if os.path.exists(BACKEND_DIR):
    if BACKEND_DIR not in sys.path:
        sys.path.insert(0, BACKEND_DIR)
    
    # Change to backend directory so relative imports work
    original_cwd = os.getcwd()
    try:
        os.chdir(BACKEND_DIR)
        # Now import from app
        from app import create_app
    except Exception as e:
        # Print error to stderr so it appears in logs
        import traceback
        print(f"Error importing app: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        raise
    finally:
        os.chdir(original_cwd)
else:
    raise ImportError(f"Backend directory not found: {BACKEND_DIR}")

# Create the application instance
# EB looks for 'application' variable
application = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    application.run(host="0.0.0.0", port=port)
