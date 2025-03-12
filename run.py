import os
from app import create_app
import logging

def main():
    """Main function to create and run the Flask app"""
    # Load environment-specific configuration
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))

    # Create the app
    app = create_app()

    # Configure logging (optional, if not fully handled in __init__.py)
    logging.basicConfig(
        level=logging.INFO if not debug else logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    app.logger.info(f"Starting Flask app in {'debug' if debug else 'production'} mode on {host}:{port}")

    # Run the app
    if os.getenv("FLASK_ENV", "development") == "development":
        app.run(host=host, port=port, debug=debug)
    else:
        app.logger.warning("Production mode detected. Use a WSGI server (e.g., Gunicorn) instead of app.run()")
        # Example for production: uncomment and adjust for your WSGI server
        # from waitress import serve
        # serve(app, host=host, port=port)

if __name__ == "__main__":
    main()