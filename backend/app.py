"""
Main Flask application
"""

from flask import Flask, jsonify
from flask_cors import CORS
from config import config
import os

# Import AWS setup function
from setup.aws_setup import setup_aws_resources

# Import blueprints
from routes.auth import auth_bp
from routes.users import users_bp
from routes.courses import courses_bp
from routes.modules import modules_bp
from routes.enrollments import enrollments_bp
from routes.progress import progress_bp
from routes.upload import upload_bp
from routes.admin import admin_bp


def create_app(config_name=None):
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Set up AWS resources (check if exists, create if not)
    # This runs automatically on app startup
    print("Initializing AWS resources...")
    success, message = setup_aws_resources(silent=False)
    if success:
        print("✓ AWS resources ready")
    else:
        print(f"⚠ {message}")
    
    # Seed initial data (admin, specializations, courses) if they don't exist
    print("Initializing database...")
    with app.app_context():
        from setup.database_seeder import seed_database
        seed_database(silent=False)
    
    # Enable CORS
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(courses_bp, url_prefix='/api/courses')
    app.register_blueprint(modules_bp, url_prefix='/api/modules')
    app.register_blueprint(enrollments_bp, url_prefix='/api/enrollments')
    app.register_blueprint(progress_bp, url_prefix='/api/progress')
    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy', 'message': 'LMS API is running'}), 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'message': 'LMS API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/health',
                'auth': '/api/auth',
                'users': '/api/users',
                'courses': '/api/courses',
                'modules': '/api/modules',
                'enrollments': '/api/enrollments',
                'progress': '/api/progress',
                'upload': '/api/upload'
            }
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

