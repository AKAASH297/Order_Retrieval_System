import flask
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_wtf import CSRFProtect

from app.config import Config
from app.models import db, User

login_manager = LoginManager()
talisman = Talisman()
limiter = Limiter(key_func=get_remote_address)
migrate = Migrate()
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'error'

    # Security headers via Flask-Talisman
    talisman.init_app(
        app,
        content_security_policy={
            'default-src': "'self'",
            'script-src': "'self'",
            'style-src': "'self' 'unsafe-inline' https://fonts.googleapis.com",
            'font-src': "'self' https://fonts.gstatic.com",
            'img-src': "'self' data:",
            'connect-src': "'self'",
        },
        force_https=False,  # Set True in production behind HTTPS
        strict_transport_security=True,
        session_cookie_secure=Config.SESSION_COOKIE_SECURE,
        session_cookie_http_only=Config.SESSION_COOKIE_HTTPONLY,
        session_cookie_samesite=Config.SESSION_COOKIE_SAMESITE,
    )

    # Rate limiting
    limiter.init_app(app)

    # CSRF protection (registers the csrf_token() template global used in
    # base.html and dashboard.html for the logout/delete buttons)
    csrf.init_app(app)

    # Database migrations
    migrate.init_app(app, db)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Make all sessions permanent (duration controlled by PERMANENT_SESSION_LIFETIME)
    @app.before_request
    def make_session_permanent():
        flask.session.permanent = True

    # Register blueprints
    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.orders import orders_bp
    app.register_blueprint(orders_bp, url_prefix='/orders')

    # Root route redirects to orders
    @app.route('/')
    def index():
        return redirect(url_for('orders.orders_page'))

    return app
