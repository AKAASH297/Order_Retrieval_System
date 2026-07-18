import os
import secrets
from datetime import timedelta


class Config:
    # Flask secret key — used to sign session cookies.
    # Set the SECRET_KEY environment variable in production.
    # Generate one with:  python -c "import secrets; print(secrets.token_hex(32))"
    # If not set, a random key is generated (sessions won't survive restarts).
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

    # SQLite database for storing app users (local file).
    # This creates a file called app.db inside the app/ directory.
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ----- MS SQL SERVER CONNECTION -----
    # The user MUST fill these in before running the app.
    # Set these via environment variables (see .env.example).
    MSSQL_SERVER = os.environ.get('MSSQL_SERVER', 'localhost')
    MSSQL_DATABASE = os.environ.get('MSSQL_DATABASE', 'TestDB')
    MSSQL_USERNAME = os.environ.get('MSSQL_USERNAME', 'sa')
    MSSQL_PASSWORD = os.environ.get('MSSQL_PASSWORD', '')
    MSSQL_PORT = int(os.environ.get('MSSQL_PORT', 1433))

    # Session security flags
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = True  # Set False for local HTTP dev

    # Session expires after 2 hours of inactivity
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)

    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s [%(levelname)s] %(name)s - %(message)s'
