import os
from dotenv import load_dotenv

load_dotenv()

try:
    from predefined_data import ADMIN_CONFIG as _ADMIN_CONFIG
except ImportError:
    _ADMIN_CONFIG = {
        'email': 'admin-moodle@ncirl.ie',
        'password': 'admin-moodle@1',
        'name': 'System Administrator',
        'role': 'admin'
    }


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN')

    DYNAMODB_USERS_TABLE = 'lms-users'
    DYNAMODB_COURSES_TABLE = 'lms-courses'
    DYNAMODB_MODULES_TABLE = 'lms-modules'
    DYNAMODB_ENROLLMENTS_TABLE = 'lms-enrollments'
    DYNAMODB_PROGRESS_TABLE = 'lms-progress'
    DYNAMODB_SPECIALIZATIONS_TABLE = 'lms-specializations'

    ADMIN_EMAIL = _ADMIN_CONFIG['email']
    ADMIN_DEFAULT_PASSWORD = _ADMIN_CONFIG['password']
    ADMIN_NAME = _ADMIN_CONFIG['name']

    S3_BUCKET_NAME = 'lms-course-materials'
    S3_REGION = os.getenv('S3_REGION', AWS_REGION)

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_HOURS = 24

    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')

    MAX_UPLOAD_SIZE = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'mp4', 'mp3'}


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

