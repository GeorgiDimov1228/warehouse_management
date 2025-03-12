import pytest
from unittest.mock import patch, MagicMock
from app.services.opcua_service import (
    read_opcua_value, write_opcua_value, opcua_log, 
    validate_node_id, is_plc_connected
)

class MockNode:
    def __init__(self, value=None):
        self.value = value
    
    def get_value(self):
        return self.value
    
    def set_value(self, value):
        self.value = value

class MockClient:
    def __init__(self, node_values=None):
        self.node_values = node_values or {}
        self.connected = True
    
    def get_node(self, node_id):
        if node_id not in self.node_values:
            self.node_values[node_id] = MockNode(0)
        return self.node_values[node_id]
    
    def connect(self):
        self.connected = True
    
    def disconnect(self):
        self.connected = False

@pytest.fixture
def mock_opcua_client():
    """Create a mock OPC UA client."""
    with patch('app.services.opcua_service.opcua_client') as mock_client_singleton:
        client = MockClient()
        mock_client_singleton.get_client.return_value = client
        mock_client_singleton.connected = True
        yield mock_client_singleton, client

def test_validate_node_id():
    """Test node ID validation."""
    # Valid node IDs
    validate_node_id("ns=2;s=TestNode")
    validate_node_id("ns=3;s=Another.Node")
    
    # Invalid node IDs
    with pytest.raises(ValueError):
        validate_node_id("invalid_node_id")
    
    with pytest.raises(ValueError):
        validate_node_id("ns=2;invalid")
    
    with pytest.raises(ValueError):
        validate_node_id(123)  # Not a string

def test_read_opcua_value(mock_opcua_client):
    """Test reading values from OPC UA."""
    mock_client_singleton, mock_client = mock_opcua_client
    
    # Set up a test node with a value
    test_node = MockNode(42)
    mock_client.node_values["ns=2;s=TestNode"] = test_node
    
    # Read the value
    value = read_opcua_value("ns=2;s=TestNode")
    assert value == 42
    
    # Read a non-existent node (should create one with default value)
    value = read_opcua_value("ns=2;s=NewNode")
    assert value == 0

def test_write_opcua_value(mock_opcua_client):
    """Test writing values to OPC UA."""
    mock_client_singleton, mock_client = mock_opcua_client
    
    # Write to a node
    result = write_opcua_value("ns=2;s=TestNode", 100)
    assert "message" in result
    
    # Read back the value to verify
    node = mock_client.get_node("ns=2;s=TestNode")
    assert node.value == 100

def test_is_plc_connected(mock_opcua_client):
    """Test checking PLC connection status."""
    mock_client_singleton, mock_client = mock_opcua_client
    
    # When connected
    connected = is_plc_connected()
    assert connected is True
    
    # When disconnected
    mock_client_singleton.connected = False
    connected = is_plc_connected()
    assert connected is False
    
    # When client is None
    mock_client_singleton.get_client.return_value = None
    connected = is_plc_connected()
    assert connected is False

@patch('app.services.opcua_service.logging')
def test_opcua_log(mock_logging):
    """Test OPC UA operation logging."""
    # Log a successful operation
    opcua_log("ns=2;s=TestNode", 42, "READ")
    mock_logging.info.assert_called_once()
    
    # Reset the mock
    mock_logging.reset_mock()
    
    # Log an error
    opcua_log("ns=2;s=TestNode", 42, "WRITE", "Test error")
    mock_logging.error.assert_called_once()

def test_connection_error(mock_opcua_client):
    """Test handling connection errors."""
    mock_client_singleton, mock_client = mock_opcua_client
    
    # Make get_client return None to simulate connection failure
    mock_client_singleton.get_client.return_value = None
    
    # Try to read a value
    result = read_opcua_value("ns=2;s=TestNode")
    assert isinstance(result, dict)
    assert "error" in result
    assert "Cannot connect to Siemens PLC" in result["error"]
    
    # Try to write a value
    result = write_opcua_value("ns=2;s=TestNode", 100)
    assert "error" in result
    assert "Cannot connect to Siemens PLC" in result["error"]

def test_invalid_node_id(mock_opcua_client):
    """Test handling invalid node IDs."""
    # Try to read with invalid node ID
    result = read_opcua_value("invalid_node")
    assert isinstance(result, dict)
    assert "error" in result
    assert "Invalid node ID format" in result["error"]
    
    # Try to write with invalid node ID
    result = write_opcua_value("invalid_node", 100)
    assert "error" in result
    assert "Invalid node ID format" in result["error"]