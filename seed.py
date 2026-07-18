"""
Run this script once to create the admin user:
    python seed.py

It is idempotent — running it again will not create duplicates.
"""
import sys
from getpass import getpass

from app import create_app
from app.models import db, User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Check if admin already exists
    existing = User.query.filter_by(username='admin').first()
    if existing:
        print('Admin user already exists. Skipping.')
    else:
        print('Creating admin user...')
        while True:
            password = getpass('Enter admin password: ')
            if len(password) < 8:
                print('Password must be at least 8 characters long.', file=sys.stderr)
                continue
            confirm = getpass('Confirm admin password: ')
            if password != confirm:
                print('Passwords do not match. Try again.', file=sys.stderr)
                continue
            break

        admin = User(
            username='admin',
            password_hash=generate_password_hash(password),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print('Admin user created successfully.')
