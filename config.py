import os

class Config:
    """Flask application configuration settings."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'teacher-workshop-dev-secret-key'
    
    # Handle Render's postgres:// prefix mismatch with SQLAlchemy 1.4+
    _database_url = os.environ.get('DATABASE_URL')
    if _database_url and _database_url.startswith("postgres://"):
        _database_url = _database_url.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = _database_url or 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or '123456'

    # Flask-Mail SMTP Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ('true', '1', 'yes')
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ('true', '1', 'yes')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@workshops.edu')
    MAIL_DEBUG = int(os.environ.get('MAIL_DEBUG', 0))

    # School contact info for email footers
    SCHOOL_NAME = os.environ.get('SCHOOL_NAME', 'School Name')
    WORKSHOP_URL = os.environ.get('WORKSHOP_URL', 'http://localhost:5000')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@school.edu')