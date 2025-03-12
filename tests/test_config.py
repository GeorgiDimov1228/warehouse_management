import pytest
import os
from unittest.mock import patch

def test_default_config(app):
    """Test the default configuration settings."""
    # Check basic Flask config
    assert app.config['TESTING'] is True
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'
    assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False
    
    # Check that required configs are present
    required_configs = ['PLC_OPC_UA_URL', 'DATABASE', 'BACKUP_DIR', 'BACKUP_INTERVAL']
    for key in required_configs:
        assert key in app.config, f"Required config key '{key}' is missing"

    # Check default OPC UA settings
    assert 'opc.tcp://' in app.config['PLC_OPC_UA_URL']
    assert 'OPCUA_ITEM_COUNT_NODE' in app.config
    assert 'OPCUA_TRAFFIC_LIGHT_NODE' in app.config

def test_environment_variable_config():
    """Test configuration from environment variables."""
    # Set some environment variables
    env_vars = {
        'FLASK_SECRET_KEY': 'test-secret-key',
        'DATABASE_URL': 'sqlite:///test.db',
        'PLC_OPC_UA_URL': 'opc.tcp://test-plc:4840',
        'BACKUP_INTERVAL': '3600'
    }
    
    with patch.dict(os.environ, env_vars):
        # Create app with environment variables
        from app import create_app
        app = create_app()
        
        # Check that environment variables were used
        assert app.config['SECRET_KEY'] == 'test-secret-key'
        assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///test.db'
        assert app.config['PLC_OPC_UA_URL'] == 'opc.tcp://test-plc:4840'
        assert app.config['BACKUP_INTERVAL'] == 3600

def test_database_path_config():
    """Test database path configuration."""
    # Test with a specific database path
    with patch.dict(os.environ, {'DATABASE': '/tmp/test-db.sqlite'}):
        from app import create_app
        app = create_app()
        
        assert app.config['DATABASE'] == '/tmp/test-db.sqlite'
        assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:////tmp/test-db.sqlite'

def test_backup_config():
    """Test backup configuration."""
    # Test with specific backup settings
    with patch.dict(os.environ, {
        'BACKUP_DIR': '/tmp/backups',
        'BACKUP_INTERVAL': '7200'
    }):
        from app import create_app
        app = create_app()
        
        assert app.config['BACKUP_DIR'] == '/tmp/backups'
        assert app.config['BACKUP_INTERVAL'] == 7200  # Should be converted to int

def test_opcua_config():
    """Test OPC UA configuration."""
    # Test with specific OPC UA settings
    with patch.dict(os.environ, {
        'PLC_OPC_UA_URL': 'opc.tcp://test-plc:4840',
        'PLC_USERNAME': 'opcuser',
        'PLC_PASSWORD': 'opcpass',
        'OPCUA_ITEM_COUNT_NODE': 'ns=3;s=CustomItemCount',
        'SYNC_ITEM_COUNT': 'False'
    }):
        from app import create_app
        app = create_app()
        
        assert app.config['PLC_OPC_UA_URL'] == 'opc.tcp://test-plc:4840'
        assert app.config['PLC_USERNAME'] == 'opcuser'
        assert app.config['PLC_PASSWORD'] == 'opcpass'
        assert app.config['OPCUA_ITEM_COUNT_NODE'] == 'ns=3;s=CustomItemCount'
        assert app.config['SYNC_ITEM_COUNT'] is False  # Should be converted to bool

def test_logging_config(app, caplog):
    """Test logging configuration."""
    # Verify logging is configured
    app.logger.info("Test log message")
    assert "Test log message" in caplog.text

def test_hmi_commands_config(app):
    """Test HMI commands configuration."""
    # Check HMI commands list
    assert 'HMI_COMMANDS' in app.config
    assert isinstance(app.config['HMI_COMMANDS'], list)
    assert 'START' in app.config['HMI_COMMANDS']
    assert 'STOP' in app.config['HMI_COMMANDS']