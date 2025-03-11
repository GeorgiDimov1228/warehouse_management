import os
import secrets

class Config:
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
    
    # OPC UA settings
    OPCUA_ENDPOINT = os.getenv("OPCUA_ENDPOINT", "opc.tcp://0.0.0.0:4840")
    OPCUA_NAMESPACE = os.getenv("OPCUA_NAMESPACE", "Warehouse")
    PLC_OPC_UA_URL = os.getenv("PLC_OPC_UA_URL", "opc.tcp://localhost:4840")
    
    # HMI Commands
    HMI_COMMANDS = ["START", "STOP", "RESET", "EMERGENCY_STOP", "LOAD", "UNLOAD", "MAINTENANCE_MODE"]