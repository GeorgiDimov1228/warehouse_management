from flask import Flask
import logging
import os
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from app.services.backup_service import start_backup_thread
from app.services.opcua_service import start_opcua_server
from app.models import db, init_db

# Load environment variables from .env file
load_dotenv()

def create_app(config_class=None):
    """Application factory with production-ready configuration"""
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Determine configuration class
    if config_class is None:
        config_type = os.getenv('FLASK_CONFIG', 'development').lower()
        
        if config_type == 'production':
            from app.config import ProductionConfig
            config_class = ProductionConfig
            # Validate production environment variables
            config_class.validate()
        elif config_type == 'testing':
            from app.config import TestingConfig
            config_class = TestingConfig
        else:
            from app.config import DevelopmentConfig
            config_class = DevelopmentConfig
    
    # Load the configuration
    app.config.from_object(config_class)
    
    # Override config with instance config when not testing
    if not app.config.get('TESTING', False):
        app.config.from_pyfile('config.py', silent=True)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    # Configure logging with rotating file handler
    if app.config.get('LOG_FILE'):
        log_dir = os.path.dirname(app.config['LOG_FILE'])
        os.makedirs(log_dir, exist_ok=True)
        
        log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
        
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'], 
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s'
        ))
        file_handler.setLevel(log_level)
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(log_level)
        
        # Also set up basic logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            handlers=[file_handler]
        )
    
    # Initialize SQLAlchemy database
    init_db(app)
    
    # Initialize database tables - only in development
    if app.config.get('FLASK_ENV') != 'production':
        with app.app_context():
            from app.services.database import initialize_database
            initialize_database()
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'environment': app.config.get('FLASK_ENV', 'unknown')}
    
    # Register blueprints
    register_blueprints(app)
    
    # Start background services if not in testing mode
    if not app.config.get('TESTING', False):
        # Start backup thread
        start_backup_thread()
        
        # Start OPC UA server
        start_opcua_server()
        
        # Start RFID listeners
        from app.services.rfid_listener import start_rfid_reader_listener
        start_rfid_reader_listener()
    
    app.logger.info(f"Application started in {app.config.get('FLASK_ENV')} mode")
    return app

def register_blueprints(app):
    """Register Flask blueprints"""
    from app.routes.auth import auth_bp
    from app.routes.product import product_bp
    from app.routes.category import category_bp
    from app.routes.opcua import opcua_bp
    from app.routes.rfid import rfid_bp
    from app.routes.cabinet import cabinet_bp
    from app.routes.rfid_extended import rfid_hw_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(opcua_bp)
    app.register_blueprint(rfid_bp)
    app.register_blueprint(cabinet_bp)
    
    # Only register RFID hardware endpoints in non-production or if simulation is enabled
    if app.config.get('ENABLE_RFID_SIMULATION', False) or app.config.get('FLASK_ENV') != 'production':
        app.register_blueprint(rfid_hw_bp)