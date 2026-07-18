from functools import wraps

from flask import render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from app.admin import admin_bp
from app.admin.forms import CreateUserForm, ResetPasswordForm
from app.models import db, User


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return abort(401)
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('orders.orders_page'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/', methods=['GET'])
@login_required
@admin_required
def dashboard():
    users = User.query.all()
    create_form = CreateUserForm()
    reset_form = ResetPasswordForm()
    return render_template('dashboard.html', users=users, create_form=create_form, reset_form=reset_form)


@admin_bp.route('/create-user', methods=['POST'])
@login_required
@admin_required
def create_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(username=form.username.data).first()
        if existing:
            current_app.logger.warning(
                'Create user failed (already exists): username=%s, admin=%s, ip=%s',
                form.username.data,
                current_user.username,
                request.remote_addr,
            )
            flash('User already exists', 'error')
            return redirect(url_for('admin.dashboard'))

        user = User(
            username=form.username.data,
            password_hash=generate_password_hash(form.password.data),
            is_admin=False
        )
        db.session.add(user)
        db.session.commit()
        current_app.logger.info(
            'User created: username=%s, by_admin=%s, ip=%s',
            form.username.data,
            current_user.username,
            request.remote_addr,
        )
        flash('User created successfully', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')

    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/delete-user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('You cannot delete your own account', 'error')
        return redirect(url_for('admin.dashboard'))

    if user.is_admin:
        flash('Cannot delete admin account', 'error')
        return redirect(url_for('admin.dashboard'))

    db.session.delete(user)
    db.session.commit()
    current_app.logger.info(
        'User deleted: username=%s, target=%s, ip=%s',
        current_user.username,
        user.username,
        request.remote_addr,
    )
    flash('User deleted successfully', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/reset-password/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    form = ResetPasswordForm()

    if form.validate_on_submit():
        user.password_hash = generate_password_hash(form.new_password.data)
        db.session.commit()
        current_app.logger.info(
            'Password reset: username=%s, target=%s, ip=%s',
            current_user.username,
            user.username,
            request.remote_addr,
        )
        flash('Password reset successfully', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')

    return redirect(url_for('admin.dashboard'))
