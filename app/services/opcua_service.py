import logging
import time
import threading
from flask import current_app
from opcua import Client
from opcua.ua import UaStatusCodeError

class OPCUAClient:
    """Singleton class to manage a persistent OPC UA client connection"""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(OPCUAClient, cls).__new__(cls)
                    cls._instance.client = None
                    cls._instance.connected = False
        return cls._instance

    def connect(self, retries=3, delay=2):
        """Connect to the Siemens PLC OPC UA server"""
        with self._lock:
            if self.connected and self.client:
                return self.client

            plc_url = current_app.config['PLC_OPC_UA_URL']
            for attempt in range(retries):
                try:
                    self.client = Client(plc_url)
                    if current_app.config.get('PLC_USERNAME') and current_app.config.get('PLC_PASSWORD'):
                        self.client.set_user(current_app.config['PLC_USERNAME'])
                        self.client.set_password(current_app.config['PLC_PASSWORD'])
                    self.client.connect()
                    self.connected = True
                    logging.info(f"Connected to Siemens PLC at {plc_url}")
                    return self.client
                except Exception as e:
                    logging.error(f"Attempt {attempt + 1}: Failed to connect to PLC: {str(e)}")
                    if attempt < retries - 1:
                        time.sleep(delay)
            logging.error("Failed to connect to Siemens PLC after all retries")
            self.client = None
            self.connected = False
            return None

    def disconnect(self):
        """Disconnect from the PLC"""
        with self._lock:
            if self.client and self.connected:
                try:
                    self.client.disconnect()
                    logging.debug("Disconnected from Siemens PLC")
                except Exception as e:
                    logging.error(f"Failed to disconnect from PLC: {str(e)}")
                finally:
                    self.client = None
                    self.connected = False

    def get_client(self):
        """Get the current client, connecting if necessary"""
        return self.connect()

# Instantiate the singleton client
opcua_client = OPCUAClient()

def validate_node_id(node_id):
    """Validate OPC UA node ID format"""
    if not isinstance(node_id, str) or not node_id.startswith("ns=") or ";s=" not in node_id:
        raise ValueError(f"Invalid node ID format: {node_id}. Expected format: 'ns=<int>;s=<string>'")

def read_opcua_value(node_id):
    """Read a value from the Siemens PLC OPC UA server"""
    client = None
    try:
        validate_node_id(node_id)
        client = opcua_client.get_client()
        if not client:
            return {"error": "Cannot connect to Siemens PLC"}
        node = client.get_node(node_id)
        value = node.get_value()
        opcua_log(node_id, value, "READ")
        return value
    except ValueError as e:
        opcua_log(node_id, None, "READ", str(e))
        return {"error": str(e)}
    except UaStatusCodeError as e:
        opcua_log(node_id, None, "READ", f"PLC status code error: {str(e)}")
        return {"error": f"PLC error: {str(e)}"}
    except Exception as e:
        opcua_log(node_id, None, "READ", str(e))
        return {"error": str(e)}

def write_opcua_value(node_id, value):
    """Write a value to the Siemens PLC OPC UA server"""
    client = None
    try:
        validate_node_id(node_id)
        client = opcua_client.get_client()
        if not client:
            return {"error": "Cannot connect to Siemens PLC"}
        node = client.get_node(node_id)
        node.set_value(value)
        opcua_log(node_id, value, "WRITE")
        return {"message": "Value written successfully"}
    except ValueError as e:
        opcua_log(node_id, value, "WRITE", str(e))
        return {"error": str(e)}
    except UaStatusCodeError as e:
        opcua_log(node_id, value, "WRITE", f"PLC status code error: {str(e)}")
        return {"error": f"PLC error: {str(e)}"}
    except Exception as e:
        opcua_log(node_id, value, "WRITE", str(e))
        return {"error": str(e)}

def opcua_log(node_id, value, status, error=None):
    """Log OPC UA operations"""
    if error:
        logging.error(f"OPC UA Failed - Node: {node_id}, Value: {value}, Status: {status}, Error: {error}")
    else:
        logging.info(f"OPC UA Update - Node: {node_id}, Value: {value}, Status: {status}")

def is_plc_connected():
    """Check if the OPC UA client is connected to the PLC"""
    client = opcua_client.get_client()
    return client is not None and opcua_client.connected

def start_opcua_server():
    """Placeholder for backward compatibility"""
    logging.info("OPC UA server initialization bypassed - operating in client-only mode")
    return None

def shutdown_opcua_client():
    """Disconnect the OPC UA client when the Flask app shuts down"""
    opcua_client.disconnect()
    logging.info("OPC UA client shutdown complete")