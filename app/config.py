import os
import secrets
from datetime import timedelta

class Config:
    """Base configuration with defaults suitable for development"""
    # Flask settings
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(32))
    
    # Database settings
    DATABASE = os.getenv("DATABASE", 'database.db')
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "False").lower() == "true"
    
    # Backup settings
    BACKUP_DIR = os.getenv("BACKUP_DIR", "backups")
    BACKUP_INTERVAL = int(os.getenv("BACKUP_INTERVAL", "86400"))  # 24 hours in seconds
    
    # Logging settings
    LOG_FILE = os.getenv("LOG_FILE", 'warehouse_log.log')
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # OPC UA settings
    OPCUA_ENDPOINT = os.getenv("OPCUA_ENDPOINT", "opc.tcp://0.0.0.0:4840")
    OPCUA_NAMESPACE = os.getenv("OPCUA_NAMESPACE", "Warehouse")
    PLC_OPC_UA_URL = os.getenv("PLC_OPC_UA_URL", "opc.tcp://localhost:4840")
    
    # HMI Commands
    HMI_COMMANDS = ["START", "STOP", "RESET", "EMERGENCY_STOP", "LOAD", "UNLOAD", "MAINTENANCE_MODE"]
    
    # RFID settings
    RFID_PRINTER_API_URL = os.getenv("RFID_PRINTER_API_URL", "http://localhost:5001/api/print")
    RFID_PRINTER_API_KEY = os.getenv("RFID_PRINTER_API_KEY", "test_api_key")
    RFID_TAG_PREFIX = os.getenv("RFID_TAG_PREFIX", "RF")
    
    # Security settings
    PASSWORD_HASH_METHOD = "pbkdf2:sha256:260000"
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
    
    # Feature flags
    ENABLE_RFID_SIMULATION = True
    
    # Multiple RFID readers configuration
    # Can be overridden completely in instance config
    RFID_READERS = {
        'entrance': {
            'url': os.getenv("RFID_READER_ENTRANCE_URL", "ws://localhost:5002/api/reader/entrance/events"),
            'api_key': os.getenv("RFID_READER_ENTRANCE_KEY", "entrance_key"),
            'location': 'Warehouse Entrance'
        },
        'exit': {
            'url': os.getenv("RFID_READER_EXIT_URL", "ws://localhost:5002/api/reader/exit/events"),
            'api_key': os.getenv("RFID_READER_EXIT_KEY", "exit_key"),
            'location': 'Warehouse Exit'
        },
        'shelf-scanner': {
            'url': os.getenv("RFID_READER_SHELF_URL", "http://localhost:5002/api/reader/shelf/scans"),
            'api_key': os.getenv("RFID_READER_SHELF_KEY", "shelf_key"),
            'polling_interval': 1.0,  # Poll every second
            'location': 'Shelf Scanner'
        }
    }


class ProductionConfig(Config):
    """Production configuration overrides"""
    # Security settings
    SESSION_COOKIE_SECURE = True  # Only send cookies over HTTPS
    
    # Feature flags for production
    ENABLE_RFID_SIMULATION = False
    SQLALCHEMY_ECHO = False
    
    # Logging - more conservative in production
    LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")
    
    # In production, keys MUST be set via environment variables
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
    RFID_PRINTER_API_KEY = os.environ.get("RFID_PRINTER_API_KEY")
    
    # Validate that critical environment variables are set
    @classmethod
    def validate(cls):
        missing_vars = []
        for var in ["FLASK_SECRET_KEY", "RFID_PRINTER_API_KEY", "DATABASE_URL"]:
            if var not in os.environ:
                missing_vars.append(var)
        
        if missing_vars:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-key-not-for-production'
    ENABLE_RFID_SIMULATION = True


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    ENABLE_RFID_SIMULATION = True
    SQLALCHEMY_ECHO = True