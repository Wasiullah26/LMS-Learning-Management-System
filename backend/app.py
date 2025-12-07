from flask import Flask, jsonify
from flask_cors import CORS
from config import config
import os
from setup.aws_setup import setup_aws_resources
from routes.auth import auth_bp
from routes.users import users_bp
from routes.courses import courses_bp
from routes.modules import modules_bp
from routes.enrollments import enrollments_bp
from routes.progress import progress_bp
from routes.upload import upload_bp
from routes.admin import admin_bp


def create_app(config_name=None):
    # Set static folder for React app (one level up from backend)
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    app = Flask(__name__, static_folder=static_dir, static_url_path='')

    config_name = config_name or os.getenv("FLASK_ENV", "development")
    app.config.from_object(config[config_name])

    # setup aws stuff when server starts
    print("Initializing AWS resources...")
    success, message = setup_aws_resources(silent=False)
    if success:
        print("✓ AWS resources ready")
    else:
        print(f"⚠ {message}")

    # enable cors for frontend
    CORS(app, origins=app.config["CORS_ORIGINS"], supports_credentials=True)

    # register all the routes
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(courses_bp, url_prefix="/api/courses")
    app.register_blueprint(modules_bp, url_prefix="/api/modules")
    app.register_blueprint(enrollments_bp, url_prefix="/api/enrollments")
    app.register_blueprint(progress_bp, url_prefix="/api/progress")
    app.register_blueprint(upload_bp, url_prefix="/api/upload")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "healthy", "message": "LMS API is running"}), 200

    @app.errorhandler(500)
    def internal_error(_error):
        return jsonify({"error": "Internal server error"}), 500

    # Custom 404 handler: serve index.html for non-API routes (React Router)
    @app.errorhandler(404)
    def not_found(error):
        from flask import request, send_from_directory
        
        # If it's an API route, return JSON error
        if request.path.startswith('/api/'):
            return jsonify({"error": "Endpoint not found"}), 404
        
        # For all other routes, serve index.html (React Router will handle routing)
        static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
        return send_from_directory(static_dir, 'index.html')

    # Serve React app root route
    @app.route('/')
    def serve_index():
        from flask import send_from_directory
        static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
        return send_from_directory(static_dir, 'index.html')

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
