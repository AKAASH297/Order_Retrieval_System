from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from app import limiter
from app.auth import auth_bp
from app.auth.forms import LoginForm, ChangePasswordForm
from app.models import db, User


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('orders.orders_page'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            current_app.logger.info(
                'Successful login: username=%s, ip=%s',
                form.username.data,
                request.remote_addr,
            )
            return redirect(url_for('orders.orders_page'))

        current_app.logger.warning(
            'Failed login attempt: username=%s, ip=%s',
            form.username.data,
            request.remote_addr,
        )
        flash('Invalid username or password', 'error')

    return render_template('login.html', form=form)


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    current_app.logger.info(
        'Logout: username=%s, ip=%s',
        current_user.username,
        request.remote_addr,
    )
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if check_password_hash(current_user.password_hash, form.current_password.data):
            current_user.password_hash = generate_password_hash(form.new_password.data)
            db.session.commit()
            current_app.logger.info(
                'Password changed: username=%s, ip=%s',
                current_user.username,
                request.remote_addr,
            )
            flash('Password changed successfully', 'success')
            return redirect(url_for('orders.orders_page'))

        current_app.logger.warning(
            'Failed password change (incorrect current password): username=%s, ip=%s',
            current_user.username,
            request.remote_addr,
        )
        flash('Current password is incorrect', 'error')

    return render_template('change_password.html', form=form)
