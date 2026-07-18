from app import create_app

app = create_app()

if __name__ == '__main__':
    # In production, use a WSGI server (gunicorn/waitress) instead.
    # See wsgi.py for the application entry point.
    app.run(debug=False, host='0.0.0.0', port=5000)
