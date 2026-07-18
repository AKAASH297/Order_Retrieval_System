from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # For non-admin users, this is the CUSTOMER value from IASCUSTOMER in MS SQL.
    # For the admin user, this is just 'admin'.
    # Must be unique — no two users can have the same username.
    username = db.Column(db.String(30), unique=True, nullable=False)

    # Hashed password. NEVER store plaintext.
    # Use werkzeug.security.generate_password_hash() to create this.
    # Use werkzeug.security.check_password_hash() to verify.
    password_hash = db.Column(db.String(256), nullable=False)

    # True only for the admin account. Regular users are False.
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    # Timestamp of when this user was created.
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
