"""
WSGI entry point for production deployment.

Run with Gunicorn (Linux):
    gunicorn wsgi:app --workers=4 --bind=0.0.0.0:5000

Run with Waitress (Windows):
    waitress-serve --port=5000 wsgi:app
"""
from app import create_app

app = create_app()
