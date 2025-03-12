from flask import Flask, redirect, url_for, session
import logging
import os
from dotenv import load_dotenv

load_dotenv()

def create_app(test_config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_object('app.config.Config')
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    required_configs = ['PLC_OPC_UA_URL', 'DATABASE', 'BACKUP_DIR', 'BACKUP_INTERVAL']
    for key in required_configs:
        if key not in app.config:
            raise ValueError(f"Required config key '{key}' is missing")

    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError as e:
        logging.error(f"Failed to create instance folder: {str(e)}")
        raise
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(os.path.join(app.instance_path, 'app.log'))
        ]
    )
    
    from app.models import db, init_db
    init_db(app)
    
    from app.routes.auth import auth_bp
    from app.routes.product import product_bp
    from app.routes.category import category_bp
    from app.routes.opcua import opcua_bp
    from app.routes.rfid import rfid_bp
    from app.routes.cabinet import cabinet_bp
    from app.routes.hmi import hmi_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(opcua_bp)
    app.register_blueprint(rfid_bp)
    app.register_blueprint(cabinet_bp)
    app.register_blueprint(hmi_bp)
    
    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('product.dashboard'))
        return redirect(url_for('auth.login'))

    @app.route('/health')
    def health_check():
        from app.services.opcua_service import is_plc_connected
        return {
            'status': 'healthy',
            'plc_connected': is_plc_connected() if not test_config else 'N/A'
        }
    
    with app.app_context():
        from app.services.database import initialize_database
        try:
            initialize_database()
        except Exception as e:
            app.logger.error(f"Database initialization error: {str(e)}")
            raise
    
    def start_services():
        from app.services.backup_service import start_backup_thread
        try:
            start_backup_thread()
        except Exception as e:
            app.logger.error(f"Backup service failed to start: {str(e)}")
            raise
        app.logger.info("Operating in OPC UA client-only mode - connecting to Siemens PLC")

    @app.teardown_appcontext
    def shutdown_services(exception=None):
        from app.services.opcua_service import shutdown_opcua_client
        try:
            shutdown_opcua_client()
        except Exception as e:
            app.logger.error(f"Error shutting down OPC UA client: {str(e)}")

    if not test_config:
        @app.before_first_request
        def initialize_services():
            start_services()

    return app