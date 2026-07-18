"""
Database queries for the orders module.

Connection pooling: uses a simple module-level queue to reuse connections
across requests, avoiding the overhead of connect/disconnect on every call.

For higher concurrency, replace this with SQLAlchemy's engine/pool:
    engine = create_engine('mssql+pymssql://...', pool_size=5, max_overflow=10)
    with engine.connect() as conn:
        ...
"""
import pymssql
from contextlib import contextmanager
from queue import Queue, Empty

from flask import current_app

# Explicit column list — prevents exposing sensitive data and
# protects against schema changes silently breaking the UI.
COLUMNS = [
    'CUSTOMER',
    'ITEM',
    'DESCRIPTION',
    'QUANTITY',
    'PRICE',
    'ORDER_DATE',
    'STATUS',
    'TOTAL_AMOUNT',
]
COLUMNS_SQL = ', '.join(COLUMNS)

# Module-level connection pool (simple Queue, thread-safe)
_pool = Queue(maxsize=5)


def _create_conn(config):
    """Create a new pymssql connection from the app config."""
    return pymssql.connect(
        server=config['MSSQL_SERVER'],
        user=config['MSSQL_USERNAME'],
        password=config['MSSQL_PASSWORD'],
        database=config['MSSQL_DATABASE'],
        port=config['MSSQL_PORT'],
        timeout=5,
        login_timeout=5,
    )


@contextmanager
def get_connection():
    """
    Context manager that borrows a connection from the pool.
    Creates a new one if the pool is empty, and returns it to
    the pool after use (unless it encountered an error).
    """
    config = current_app.config
    try:
        conn = _pool.get_nowait()
        # Quick health check
        conn.cursor().execute('SELECT 1')
    except (Empty, Exception):
        conn = _create_conn(config)

    try:
        yield conn
    except Exception:
        conn.close()
        current_app.logger.exception('Database connection error')
        raise
    else:
        try:
            _pool.put_nowait(conn)
        except Exception:
            conn.close()


def get_orders_for_customer(customer_value):
    """
    Queries IASSALITEM where CUSTOMER = customer_value,
    returning (column_names, rows).

    Uses a connection from the module-level pool so connections
    are reused across requests rather than created/destroyed each time.

    Returns:
        column_names: list of strings (column headers)
        rows: list of tuples (each tuple is a row)

    Raises:
        Exception on connection or query failure.
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        # CRITICAL: Use parameterized query (%s) to prevent SQL injection.
        # Do NOT use string formatting or f-strings to build this query.
        cursor.execute(
            f"SELECT {COLUMNS_SQL} FROM IASSALITEM WHERE CUSTOMER = %s",
            (customer_value,),
        )

        column_names = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        return column_names, rows
