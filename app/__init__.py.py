from flask import Flask
import logging
import os
from dotenv import load_dotenv
from app.services.backup_service import start_backup_thread
from app.services.opcua_service import start_opcua_server
from app.models import db, init_db

# Load environment variables from .env file
load_dotenv()

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Load the default configuration
    app.config.from_object('app.config.Config')
    
    # Override config with instance config when not testing
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    # Configure logging
    logging.basicConfig(
        filename=app.config['LOG_FILE'],
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Initialize SQLAlchemy database
    init_db(app)
    
    # Initialize database tables
    with app.app_context():
        from app.services.database import initialize_database
        initialize_database()
    
    # Start backup thread
    start_backup_thread()
    
    # Start OPC UA server
    start_opcua_server()
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.product import product_bp
    from app.routes.category import category_bp
    from app.routes.opcua import opcua_bp
    from app.routes.rfid import rfid_bp
    from app.routes.cabinet import cabinet_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(opcua_bp)
    app.register_blueprint(rfid_bp)
    app.register_blueprint(cabinet_bp)
    
    # A simple route to check if the app is running
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}
    
    return app