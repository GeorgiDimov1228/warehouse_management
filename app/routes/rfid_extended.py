from flask import Blueprint, request, jsonify, session
from app.services.rfid_service import (
    encode_rfid_tag, process_rfid_scan, 
    simulate_rfid_scan, RFIDPrinterException, RFIDReaderException
)
from app.models import db
from app.models.product import Product
from app.models.transaction import RFIDTracking
import logging

rfid_hw_bp = Blueprint('rfid_hardware', __name__, url_prefix='/rfid-hardware')

@rfid_hw_bp.route('/print-tag', methods=['POST'])
def print_rfid_tag():
    """Print and encode a new RFID tag for a product"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.json
    product_id = data.get('product_id')
    custom_tag = data.get('rfid_tag')  # Optional
    
    if not product_id:
        return jsonify({'error': 'Missing product_id'}), 400
    
    try:
        # Verify the product exists
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': f'Product with ID {product_id} not found'}), 404
        
        # Encode and print the tag
        rfid_tag = encode_rfid_tag(product_id, custom_tag)
        
        return jsonify({
            'success': True,
            'message': 'RFID tag printed successfully',
            'product_id': product_id,
            'rfid_tag': rfid_tag
        })
    except RFIDPrinterException as e:
        logging.error(f"RFID printing error: {str(e)}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        logging.error(f"Unexpected error in print_rfid_tag: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@rfid_hw_bp.route('/batch-print', methods=['POST'])
def batch_print_rfid_tags():
    """Print and encode multiple RFID tags in batch"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.json
    product_ids = data.get('product_ids', [])
    
    if not product_ids:
        return jsonify({'error': 'No product_ids provided'}), 400
    
    results = {
        'success': [],
        'failures': []
    }
    
    for product_id in product_ids:
        try:
            rfid_tag = encode_rfid_tag(product_id)
            results['success'].append({
                'product_id': product_id,
                'rfid_tag': rfid_tag
            })
        except Exception as e:
            results['failures'].append({
                'product_id': product_id,
                'error': str(e)
            })
    
    return jsonify({
        'success': len(results['success']) > 0,
        'total': len(product_ids),
        'successful': len(results['success']),
        'failed': len(results['failures']),
        'results': results
    })

@rfid_hw_bp.route('/reader/<reader_id>/scan', methods=['POST'])
def reader_scan(reader_id):
    """Handle RFID scan from a specific reader"""
    # This endpoint would be called by the RFID reader hardware
    # In a real implementation, this would likely use authentication specific to the reader
    data = request.json
    rfid_tags = data.get('rfid_tags', [])
    
    if not rfid_tags:
        return jsonify({'error': 'No RFID tags provided'}), 400
    
    try:
        results = process_rfid_scan(reader_id, rfid_tags)
        return jsonify(results)
    except Exception as e:
        logging.error(f"Error processing RFID scan: {str(e)}")
        return jsonify({'error': str(e)}), 500

@rfid_hw_bp.route('/simulate-scan', methods=['POST'])
def simulate_scan():
    """Simulate an RFID scan for testing purposes"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.json
    reader_id = data.get('reader_id', 'test-reader')
    rfid_tags = data.get('rfid_tags', [])
    
    if not rfid_tags:
        return jsonify({'error': 'No RFID tags provided'}), 400
    
    try:
        results = simulate_rfid_scan(reader_id, rfid_tags)
        return jsonify(results)
    except Exception as e:
        logging.error(f"Error simulating RFID scan: {str(e)}")
        return jsonify({'error': str(e)}), 500

@rfid_hw_bp.route('/inventory', methods=['GET'])
def rfid_inventory():
    """Get complete RFID inventory"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    inventory = []
    products = Product.query.filter(Product.rfid_tag.isnot(None)).all()
    
    for product in products:
        # Get the most recent tracking status for this product
        latest_tracking = RFIDTracking.query.filter_by(
            product_id=product.id
        ).order_by(
            RFIDTracking.timestamp.desc()
        ).first()
        
        inventory.append({
            'product_id': product.id,
            'product_name': product.name,
            'rfid_tag': product.rfid_tag,
            'category_id': product.category_id,
            'last_status': latest_tracking.status if latest_tracking else None,
            'last_updated': latest_tracking.timestamp.isoformat() if latest_tracking else None
        })
    
    return jsonify({
        'count': len(inventory),
        'inventory': inventory
    })

@rfid_hw_bp.route('/tag-history/<rfid_tag>', methods=['GET'])
def tag_history(rfid_tag):
    """Get the history of a specific RFID tag"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    if not rfid_tag:
        return jsonify({'error': 'RFID tag is required'}), 400
    
    # Find the product associated with this tag
    product = Product.query.filter_by(rfid_tag=rfid_tag).first()
    if not product:
        return jsonify({'error': 'RFID tag not found'}), 404
    
    # Get all tracking records for this tag
    tracking_records = RFIDTracking.query.filter_by(
        rfid_tag=rfid_tag
    ).order_by(
        RFIDTracking.timestamp.desc()
    ).all()
    
    history = []
    for record in tracking_records:
        history.append({
            'timestamp': record.timestamp.isoformat(),
            'status': record.status,
            'shelf_id': record.shelf_id,
            'id': record.id
        })
    
    return jsonify({
        'product_id': product.id,
        'product_name': product.name,
        'rfid_tag': rfid_tag,
        'history_count': len(history),
        'history': history
    })