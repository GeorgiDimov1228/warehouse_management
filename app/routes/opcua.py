from flask import Blueprint, request, jsonify, session, current_app
from app.services.opcua_service import read_opcua_value, write_opcua_value, opcua_client, is_plc_connected
from app.models import db
from app.models.product import Product
import logging
from sqlalchemy import func
from functools import wraps

opcua_bp = Blueprint('opcua', __name__, url_prefix='/opcua')

def require_auth(f):
    """Decorator to enforce authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated

@opcua_bp.route('/status', methods=['GET'])
def opcua_status():
    """Check OPC UA connection status"""
    try:
        connected = is_plc_connected()
        return jsonify({'status': 'Connected' if connected else 'Disconnected'})
    except Exception as e:
        logging.error(f"Error in OPC UA status check: {str(e)}")
        return jsonify({'status': 'Error', 'error': str(e)}), 500

@opcua_bp.route('/read', methods=['POST'])
@require_auth
def opcua_read():
    """Read a value from OPC UA server"""
    data = request.get_json()
    node_id = data.get('node_id')
    
    if not node_id:
        return jsonify({'error': 'Missing node_id parameter'}), 400
    
    result = read_opcua_value(node_id)
    if isinstance(result, dict) and 'error' in result:
        return jsonify(result), 500
    
    return jsonify({'node_id': node_id, 'value': result})

@opcua_bp.route('/write', methods=['POST'])
@require_auth
def opcua_write():
    """Write a value to OPC UA server"""
    data = request.get_json()
    node_id = data.get('node_id')
    value = data.get('value')
    
    if not node_id or value is None:
        return jsonify({'error': 'Missing node_id or value parameter'}), 400
    
    result = write_opcua_value(node_id, value)
    if 'error' in result:
        return jsonify(result), 500
    
    return jsonify({'node_id': node_id, **result})

@opcua_bp.route('/get-item-count', methods=['GET'])
def get_item_count():
    """Get item count from database and optionally sync with OPC UA"""
    try:
        total_count = db.session.query(func.sum(Product.quantity)).scalar() or 0
        
        # Sync with OPC UA if configured
        if current_app.config.get('SYNC_ITEM_COUNT', True):
            result = write_opcua_value(current_app.config.get('OPCUA_ITEM_COUNT_NODE', 'ns=2;s=ItemCount'), total_count)
            if 'error' in result:
                logging.warning(f"Failed to sync ItemCount to OPC UA: {result['error']}")
        
        return jsonify({'item_count': total_count})
    except Exception as e:
        logging.error(f"Error getting item count: {str(e)}")
        return jsonify({'error': str(e)}), 500

@opcua_bp.route('/set-item-count', methods=['POST'])
@require_auth
def set_item_count():
    """Set item count in OPC UA"""
    data = request.get_json()
    new_count = data.get('item_count')
    
    if not isinstance(new_count, int) or new_count < 0:
        return jsonify({'error': 'Item count must be a non-negative integer'}), 400
    
    node_id = current_app.config.get('OPCUA_ITEM_COUNT_NODE', 'ns=2;s=ItemCount')
    result = write_opcua_value(node_id, new_count)
    if 'error' in result:
        return jsonify(result), 500
    
    return jsonify({'message': 'Item count updated successfully', 'item_count': new_count})

@opcua_bp.route('/get-traffic-light', methods=['GET'])
def get_traffic_light_status():
    """Get traffic light status from OPC UA"""
    node_id = current_app.config.get('OPCUA_TRAFFIC_LIGHT_NODE', 'ns=2;s=TrafficLightStatus')
    result = read_opcua_value(node_id)
    if isinstance(result, dict) and 'error' in result:
        return jsonify(result), 500
    
    return jsonify({'traffic_light_status': result})

@opcua_bp.route('/set-traffic-light', methods=['POST'])
@require_auth
def set_traffic_light_status():
    """Set traffic light status in OPC UA"""
    data = request.get_json()
    new_status = data.get('traffic_light_status')
    
    valid_statuses = ['RED', 'YELLOW', 'GREEN', 'OFF']
    if new_status not in valid_statuses:
        return jsonify({'error': f"Invalid status. Must be one of {valid_statuses}"}), 400
    
    node_id = current_app.config.get('OPCUA_TRAFFIC_LIGHT_NODE', 'ns=2;s=TrafficLightStatus')
    result = write_opcua_value(node_id, new_status)
    if 'error' in result:
        return jsonify(result), 500
    
    return jsonify({'message': 'Traffic light status updated successfully', 'traffic_light_status': new_status})

@opcua_bp.route('/get-hmi-status', methods=['GET'])
def get_hmi_status():
    """Get HMI status from OPC UA"""
    node_id = current_app.config.get('OPCUA_HMI_STATUS_NODE', 'ns=2;s=HMIStatus')
    result = read_opcua_value(node_id)
    if isinstance(result, dict) and 'error' in result:
        return jsonify(result), 500
    
    return jsonify({'hmi_status': result})

@opcua_bp.route('/set-hmi-command', methods=['POST'])
@require_auth
def set_hmi_command():
    """Set HMI command in OPC UA"""
    data = request.get_json()
    new_command = data.get('hmi_command')
    
    valid_commands = current_app.config.get('HMI_COMMANDS', ['NONE', 'START', 'STOP', 'RESET'])
    if not isinstance(new_command, str) or new_command not in valid_commands:
        return jsonify({'error': f"Invalid HMI command. Must be one of {valid_commands}"}), 400
    
    node_id = current_app.config.get('OPCUA_HMI_COMMAND_NODE', 'ns=2;s=HMICommand')
    result = write_opcua_value(node_id, new_command)
    if 'error' in result:
        return jsonify(result), 500
    
    return jsonify({'message': 'HMI command updated successfully', 'hmi_command': new_command})

@opcua_bp.route('/update', methods=['POST'])
@require_auth
def opcua_update():
    """Update a node in OPC UA server"""
    data = request.get_json()
    node_id = data.get('node_id')
    value = data.get('value')
    
    if not node_id or value is None:
        return jsonify({'error': 'Missing node_id or value parameter'}), 400
    
    result = write_opcua_value(node_id, value)
    if 'error' in result:
        return jsonify(result), 500
    
    return jsonify({'message': 'OPC UA node updated successfully', 'node_id': node_id, 'value': value})

@opcua_bp.route('/sync-inventory', methods=['POST'])
@require_auth
def sync_inventory():
    """Sync inventory data between database and OPC UA"""
    try:
        total_quantity = db.session.query(func.sum(Product.quantity)).scalar() or 0
        
        item_node = current_app.config.get('OPCUA_ITEM_COUNT_NODE', 'ns=2;s=ItemCount')
        result = write_opcua_value(item_node, total_quantity)
        if 'error' in result:
            logging.warning(f"Failed to sync ItemCount: {result['error']}")

        top_categories = db.session.query(
            Product.category_id,
            func.count(Product.id).label('count')
        ).group_by(Product.category_id).order_by(func.count(Product.id).desc()).limit(3).all()
        
        category_data = ','.join([f"{cat[0]}:{cat[1]}" for cat in top_categories if cat[0]])
        cat_node = current_app.config.get('OPCUA_CATEGORY_DATA_NODE', 'ns=2;s=CategoryData')
        result = write_opcua_value(cat_node, category_data)
        if 'error' in result:
            logging.warning(f"Failed to sync CategoryData: {result['error']}")
        
        return jsonify({
            'message': 'Inventory data synced with OPC UA',
            'total_quantity': total_quantity,
            'category_data': category_data
        })
    except Exception as e:
        logging.error(f"Error syncing inventory data: {str(e)}")
        return jsonify({'error': str(e)}), 500