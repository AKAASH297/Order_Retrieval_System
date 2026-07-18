from datetime import datetime
from decimal import Decimal

from flask import render_template, jsonify, current_app
from flask_login import login_required, current_user

from app.orders import orders_bp
from app.orders.queries import get_orders_for_customer


def serialize_value(val):
    """Convert non-JSON-serializable types to strings."""
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.isoformat()
    if isinstance(val, Decimal):
        return float(val)
    return val


def serialize_rows(rows):
    """Convert all cells in all rows to JSON-serializable values."""
    return [[serialize_value(cell) for cell in row] for row in rows]


@orders_bp.route('/')
@login_required
def orders_page():
    return render_template('orders.html')


@orders_bp.route('/fetch')
@login_required
def fetch_orders():
    if current_user.is_admin:
        return jsonify({
            'error': 'Admin account does not have an associated customer. Please log in as a regular user.'
        }), 400

    try:
        column_names, rows = get_orders_for_customer(current_user.username)
        return jsonify({
            'columns': column_names,
            'rows': serialize_rows(rows)
        })
    except Exception:
        current_app.logger.exception('Failed to fetch orders for user %s', current_user.username)
        return jsonify({'error': 'An error occurred while fetching orders. Please try again later.'}), 500
