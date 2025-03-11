from flask import Blueprint, request, jsonify, current_app, session
from app.services.opcua_service import read_opcua_value, write_opcua_value, connect_opcua_client, opcua_log
from app.models import db
from app.models.product import Product
import logging
from sqlalchemy import func

opcua_bp = Blueprint('opcua', __name__, url_prefix='/opcua')

@opcua_bp.route('/status', methods=['GET'])
def opcua_status():
    """Check OPC UA connection status"""
    # Verify authentication for sensitive operations
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
        
    client = connect_opcua_client()
    if client:
        client.disconnect()
        return jsonify({'status': 'Connected'})
    
    logging.warning("Failed to connect to OPC UA server")
    return jsonify({'status': 'Disconnected', 'error': 'Cannot connect to OPC UA server'})

@opcua_bp.route('/read', methods=['POST'])
def opcua_read():
    """Read a value from OPC UA server"""
    # Verify authentication for sensitive operations
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
        
    data = request.json
    node_id = data.get('node_id')
    
    if not node_id:
        return jsonify({'error': 'Missing node_id parameter'}), 400
    
    result = read_opcua_value(node_id)
    if isinstance(result, dict) and 'error' in result:
        logging.error(f"Error reading OPC UA node {node_id}: {result['error']}")
        return jsonify(result), 500
    
    logging.info(f"Successfully read OPC UA node {node_id}: {result}")
    return jsonify({'value': result})

@opcua_bp.route('/write', methods=['POST'])
def opcua_write():
    """Write a value to OPC UA server"""
    # Verify authentication for sensitive operations
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
        
    data = request.json
    node_id = data.get('node_id')
    value = data.get('value')
    
    if not node_id or value is None:
        return jsonify({'error': 'Missing node_id or value parameter'}), 400
    
    result = write_opcua_value(node_id, value)
    if 'error' in result:
        logging.error(f"Error writing to OPC UA node {node_id}: {result['error']}")
        return jsonify(result), 500
    
    logging.info(f"Successfully wrote to OPC UA node {node_id}: {value}")
    return jsonify(result)

@opcua_bp.route('/get-item-count', methods=['GET'])
def get_item_count():
    """Get item count from OPC UA"""
    # For item count, we'll use the database directly
    total_count = db.session.query(func.sum(Product.quantity)).scalar() or 0
    
    # Also update the OPC UA server with this value
    try:
        write_opcua_value('ns=2;s=ItemCount', total_count)
    except Exception as e:
        logging.warning(f"Failed to update OPC UA ItemCount: {str(e)}")
    
    return jsonify({'item_count': total_count})

@opcua_bp.route('/set-item-count', methods=['POST'])
def set_item_count():
    """Set item count in OPC UA"""
    # Verify authentication for sensitive operations
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
        
    data = request.json
    new_count = data.get('item_count')
    
    if not isinstance(new_count, int):
        return jsonify({'error': 'Invalid item count'}), 400
    
    result = write_opcua_value('ns=2;s=ItemCount', new_count)
    if 'error' in result:
        logging.error(f"Error updating item count in OPC UA: {result['error']}")
        return jsonify(result), 500
    
    logging.info(f"Item count updated in OPC UA: {new_count}")
    return jsonify({'message': 'Item count updated successfully'})

@opcua_bp.route('/get-traffic-light', methods=['GET'])
def get_traffic_light_status():
    """Get traffic light status from OPC UA"""
    # This endpoint could be used without authentication for display purposes
    result = read_opcua_value('ns=2;s=TrafficLightStatus')
    if isinstance(result, dict) and 'error' in result:
        logging.error(f"Error reading traffic light status: {result['error']}")
        return jsonify(result), 500
    
    return jsonify({'traffic_light_status': result})

@opcua_bp.route('/set-traffic-light', methods=['POST'])
def set_traffic_light_status():
    """Set traffic light status in OPC UA"""
    # Verify authentication for sensitive operations
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
        
    data = request.json
    new_status = data.get('traffic_light_status')
    
    if new_status not in ['RED', 'YELLOW', 'GREEN', 'OFF']:
        return jsonify({'error': 'Invalid status'}), 400
    
    result = write_opcua_value('ns=2;s=TrafficLightStatus', new_status)
    if 'error' in result:
        logging.error(f"Error setting traffic light status: {result['error']}")
        return jsonify(result), 500
    
    logging.info(f"Traffic light status updated to: {new_status}")
    return jsonify({'message': 'Traffic light status updated successfully'})

@opcua_bp.route('/get-hmi-status', methods=['GET'])
def get_hmi_status():
    """Get HMI status from OPC UA"""
    # This endpoint could be used without authentication for display purposes
    result = read_opcua_value('ns=2;s=HMIStatus')
    if isinstance(result, dict) and 'error' in result:
        logging.error(f"Error reading HMI status: {result['error']}")
        return jsonify(result), 500
    
    return jsonify({'hmi_status': result})

@opcua_bp.route('/set-hmi-command', methods=['POST'])
def set_hmi_command():
    """Set HMI command in OPC UA"""
    # Verify authentication for sensitive operations
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
        
    data = request.json
    new_command = data.get('hmi_command')
    
    if not isinstance(new_command, str) or new_command not in current_app.config['HMI_COMMANDS']:
        return jsonify({'error': 'Invalid HMI command'}), 400
    
    result = write_opcua_value('ns=2;s=HMICommand', new_command)
    if 'error' in result:
        logging.error(f"Error setting HMI command: {result['error']}")
        return jsonify(result), 500
    
    logging.info(f"HMI command updated to: {new_command}")
    return jsonify({'message': 'HMI command updated successfully'})

@opcua_bp.route('/update', methods=['POST'])
def opcua_update():
    """Update a node in OPC UA server"""
    # Verify authentication for sensitive operations
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
        
    data = request.json
    node_id = data.get('node_id')
    value = data.get('value')
    
    if not node_id or value is None:
        return jsonify({'error': 'Invalid node_id or value'}), 400
    
    result = write_opcua_value(node_id, value)
    if 'error' in result:
        opcua_log(node_id, value, 'Failed', result['error'])
        return jsonify(result), 500
    
    opcua_log(node_id, value, 'Success')
    return jsonify({'message': 'OPC UA updated successfully'})

@opcua_bp.route('/sync-inventory', methods=['POST'])
def sync_inventory():
    """Sync inventory data between database and OPC UA"""
    # Verify authentication for sensitive operations
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Get total quantity from database
        total_quantity = db.session.query(func.sum(Product.quantity)).scalar() or 0
        
        # Update OPC UA item count
        write_opcua_value('ns=2;s=ItemCount', total_quantity)
        
        # Get top 3 categories by product count to show on HMI display
        top_categories = db.session.query(
            Product.category_id, 
            func.count(Product.id).label('count')
        ).group_by(
            Product.category_id
        ).order_by(
            func.count(Product.id).desc()
        ).limit(3).all()
        
        category_data = ','.join([f"{cat[0]}:{cat[1]}" for cat in top_categories if cat[0]])
        
        # Update category data in OPC UA
        write_opcua_value('ns=2;s=CategoryData', category_data)
        
        logging.info(f"Inventory data synced with OPC UA: Items={total_quantity}, Categories={category_data}")
        return jsonify({
            'message': 'Inventory data synced with OPC UA',
            'total_quantity': total_quantity,
            'category_data': category_data
        })
    except Exception as e:
        logging.error(f"Error syncing inventory data: {str(e)}")
        return jsonify({'error': f'Error syncing inventory data: {str(e)}'}), 500