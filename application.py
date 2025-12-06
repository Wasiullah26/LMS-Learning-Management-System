import sys
import os

# Get the directory where this file is located
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, 'backend')

# Add backend directory to Python path so imports work
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Also add the parent directory for relative imports
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Now import from app (which is in backend/app.py)
from app import create_app

# EB looks for 'application' by default
application = create_app()

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

