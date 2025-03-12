import os
import secrets

class Config:
    # Flask settings
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(32))
    
    # Database settings
    DATABASE = os.getenv("DATABASE", os.path.join(os.path.dirname(__file__), '..', 'instance', 'database.db'))
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "False").lower() == "true"
    
    # Backup settings
    BACKUP_DIR = os.getenv("BACKUP_DIR", os.path.join(os.path.dirname(__file__), '..', 'instance', 'backups'))
    BACKUP_INTERVAL = int(os.getenv("BACKUP_INTERVAL", "86400"))  # 24 hours in seconds
    
    # Logging settings
    LOG_FILE = os.getenv("LOG_FILE", os.path.join(os.path.dirname(__file__), '..', 'instance', 'warehouse_log.log'))
    
    # OPC UA settings
    PLC_OPC_UA_URL = os.getenv("PLC_OPC_UA_URL", "opc.tcp://localhost:4840")
    PLC_USERNAME = os.getenv("PLC_USERNAME")
    PLC_PASSWORD = os.getenv("PLC_PASSWORD")
    OPCUA_ITEM_COUNT_NODE = os.getenv("OPCUA_ITEM_COUNT_NODE", "ns=2;s=ItemCount")
    OPCUA_TRAFFIC_LIGHT_NODE = os.getenv("OPCUA_TRAFFIC_LIGHT_NODE", "ns=2;s=TrafficLightStatus")
    OPCUA_HMI_STATUS_NODE = os.getenv("OPCUA_HMI_STATUS_NODE", "ns=2;s=HMIStatus")
    OPCUA_HMI_COMMAND_NODE = os.getenv("OPCUA_HMI_COMMAND_NODE", "ns=2;s=HMICommand")
    OPCUA_CATEGORY_DATA_NODE = os.getenv("OPCUA_CATEGORY_DATA_NODE", "ns=2;s=CategoryData")
    SYNC_ITEM_COUNT = os.getenv("SYNC_ITEM_COUNT", "True").lower() == "true"
    
    # HMI Commands
    HMI_COMMANDS = ["START", "STOP", "RESET", "EMERGENCY_STOP", "LOAD", "UNLOAD", "MAINTENANCE_MODE"]