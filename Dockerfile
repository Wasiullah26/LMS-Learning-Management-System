# Multi-stage build for LMS application

# Stage 1: Build Frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY frontend/ .

# Build React app with API URL (defaults to relative path for same origin)
# If you want to use a different API URL, set VITE_API_URL during build
ARG VITE_API_URL=/api
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build

# Stage 2: Backend with Frontend
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/dist ./static

# Create application entry point
RUN echo 'import sys, os\n\
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))\n\
from app import create_app\n\
application = create_app()\n\
if __name__ == "__main__":\n\
    application.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))' > application.py

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')" || exit 1

# Run with Gunicorn
CMD ["gunicorn", "application:application", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120"]

