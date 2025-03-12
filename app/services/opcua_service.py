import logging
import time
from flask import current_app
from opcua import Client

def connect_opcua_client(retries=3, delay=2):
    """Connect to the OPC UA server with retry logic"""
    for attempt in range(retries):
        try:
            client = Client(current_app.config['PLC_OPC_UA_URL'])
            client.connect()
            logging.info(f"Connected to OPC UA server at {current_app.config['PLC_OPC_UA_URL']}")
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