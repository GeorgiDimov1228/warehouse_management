import logging
import threading
import time
from flask import current_app
# Import from opcua library directly
from opcua import Server, Client

# Global variable to store the OPC UA server
opcua_server = None
opcua_variables = {}

def initialize_opcua_server():
    """Initialize and configure the OPC UA server"""
    global opcua_server, opcua_variables
    
    try:
        # Create a new server instance
        opcua_server = Server()
        opcua_server.set_endpoint(current_app.config['OPCUA_ENDPOINT'])
        
        # Register a namespace
        opcua_namespace = opcua_server.register_namespace(current_app.config['OPCUA_NAMESPACE'])
        
        # Create an OPC UA object for warehouse management
        warehouse_obj = opcua_server.nodes.objects.add_object(opcua_namespace, "Warehouse")
        
        # Create variables for inventory management
        opcua_variables['item_count'] = warehouse_obj.add_variable(opcua_namespace, "ItemCount", 0)
        opcua_variables['traffic_light_status'] = warehouse_obj.add_variable(opcua_namespace, "TrafficLightStatus", "OFF")
        opcua_variables['hmi_command'] = warehouse_obj.add_variable(opcua_namespace, "HMICommand", "NONE")
        opcua_variables['hmi_status'] = warehouse_obj.add_variable(opcua_namespace, "HMIStatus", "IDLE")
        
        # Allow variables to be modified
        opcua_variables['item_count'].set_writable()
        opcua_variables['traffic_light_status'].set_writable()
        opcua_variables['hmi_command'].set_writable()
        opcua_variables['hmi_status'].set_writable()
        
        logging.info("OPC UA server initialized")
        return opcua_server
    except Exception as e:
        logging.error(f"Error initializing OPC UA server: {str(e)}")
        return None

def run_opcua_server():
    """Run the OPC UA server"""
    global opcua_server
    
    try:
        if opcua_server is None:
            logging.info("Initializing OPC UA server...")
            opcua_server = initialize_opcua_server()
        
        if opcua_server:
            opcua_server.start()
            logging.info(f"OPC UA Server started at {current_app.config['OPCUA_ENDPOINT']}")
            
            # Keep the server running
            while True:
                time.sleep(1)
        else:
            logging.error("Failed to initialize OPC UA server")
    except Exception as e:
        logging.error(f"OPC UA Server error: {str(e)}")
    finally:
        try:
            if opcua_server:
                opcua_server.stop()
                logging.info("OPC UA Server stopped")
        except Exception as e:
            logging.error(f"Error stopping OPC UA server: {str(e)}")

def start_opcua_server():
    """Start the OPC UA server in a separate thread"""
    try:
        # Create and start the thread
        server_thread = threading.Thread(target=run_opcua_server, daemon=True)
        server_thread.start()
        logging.info("OPC UA server thread started")
        return server_thread
    except Exception as e:
        logging.error(f"Failed to start OPC UA server thread: {str(e)}")
        return None

def connect_opcua_client(retries=3, delay=2):
    """Connect to the OPC UA server with retry logic"""
    for attempt in range(retries):
        try:
            client = Client(current_app.config['PLC_OPC_UA_URL'])
            client.connect()
            logging.info("Connected to OPC UA server")
            return client
        except Exception as e:
            logging.error(f"Attempt {attempt + 1}: Failed to connect to OPC UA server: {str(e)}")
            if attempt < retries - 1:
                time.sleep(delay)
    
    return None

def read_opcua_value(node_id):
    """Read a value from the OPC UA server"""
    client = None
    try:
        client = connect_opcua_client()
        if not client:
            return {"error": "Cannot connect to OPC UA server"}
        
        node = client.get_node(node_id)
        value = node.get_value()
        logging.info(f"Read from OPC UA - Node: {node_id}, Value: {value}")
        return value
    except Exception as e:
        logging.error(f"Failed to read OPC UA node {node_id}: {str(e)}")
        return {"error": str(e)}
    finally:
        if client:
            try:
                client.disconnect()
            except:
                pass

def write_opcua_value(node_id, value):
    """Write a value to the OPC UA server"""
    client = None
    try:
        client = connect_opcua_client()
        if not client:
            return {"error": "Cannot connect to OPC UA server"}
        
        node = client.get_node(node_id)
        node.set_value(value)
        logging.info(f"Write to OPC UA - Node: {node_id}, Value: {value}")
        return {"message": "Value written successfully"}
    except Exception as e:
        logging.error(f"Failed to write OPC UA node {node_id}: {str(e)}")
        return {"error": str(e)}
    finally:
        if client:
            try:
                client.disconnect()
            except:
                pass

def opcua_log(node_id, value, status, error=None):
    """Log OPC UA operations"""
    if error:
        logging.error(f"OPC UA Failed - Node: {node_id}, Value: {value}, Status: {status}, Error: {error}")
    else:
        logging.info(f"OPC UA Update - Node: {node_id}, Value: {value}, Status: {status}")