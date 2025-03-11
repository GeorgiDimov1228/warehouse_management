from flask import Blueprint, request, jsonify
from app.models import db
from app.models.user import User
from app.models.product import Product
from app.models.transaction import Transaction, RFIDTracking
import logging

rfid_bp = Blueprint('rfid', __name__, url_prefix='/rfid')

@rfid_bp.route('/auth', methods=['POST'])
def rfid_auth():
    """Authenticate using RFID tag"""
    data = request.json
    rfid_tag = data.get('rfid_tag')
    
    if not rfid_tag:
        return jsonify({'error': 'Missing RFID tag'}), 400
    
    user = User.query.filter_by(rfid_tag=rfid_tag).first()
    
    if user:
        logging.info(f"RFID authenticated for user ID: {user.id}")
        return jsonify({
            'message': 'RFID authenticated',
            'user_id': user.id,
            'username': user.username
        })
    
    logging.warning(f"Unauthorized RFID attempt: {rfid_tag}")
    return jsonify({'error': 'Unauthorized RFID'}), 401

@rfid_bp.route('/load', methods=['POST'])
def load_items():
    """Load items using RFID tag"""
    data = request.json
    rfid_tag = data.get('rfid_tag')
    product_rfid = data.get('product_rfid')
    quantity = data.get('quantity', 1)
    shelf_id = data.get('shelf_id')
    
    # Validate input
    if not rfid_tag or not product_rfid:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # First verify the user
    user = User.query.filter_by(rfid_tag=rfid_tag).first()
    
    if not user:
        logging.warning(f"Unauthorized RFID attempt during item load: {rfid_tag}")
        return jsonify({'error': 'Unauthorized RFID'}), 401
    
    # Then get the product
    product = Product.query.filter_by(rfid_tag=product_rfid).first()
    
    if not product:
        logging.warning(f"Unknown product RFID: {product_rfid}")
        return jsonify({'error': 'Product RFID tag not found'}), 404
    
    try:
        # Update the product quantity
        product.quantity += quantity
        
        # Create transaction record
        transaction = Transaction(
            user_id=user.id,
            product_id=product.id,
            quantity=quantity,
            transaction_type='load',
            shelf_id=shelf_id
        )
        db.session.add(transaction)
        
        # Create RFID tracking record
        tracking = RFIDTracking(
            rfid_tag=product_rfid,
            product_id=product.id,
            shelf_id=shelf_id,
            status='added'
        )
        db.session.add(tracking)
        
        db.session.commit()
        logging.info(f"Item loaded: Product ID {product.id}, Quantity {quantity}, User ID {user.id}")
        return jsonify({
            'message': 'Item loaded successfully',
            'product_name': product.name,
            'new_quantity': product.quantity
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error loading item: {str(e)}")
        return jsonify({'error': f'Error loading item: {str(e)}'}), 500

@rfid_bp.route('/get', methods=['POST'])
def get_items():
    """Get items using RFID tag"""
    data = request.json
    rfid_tag = data.get('rfid_tag')
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    shelf_id = data.get('shelf_id')
    
    # Validate input
    if not rfid_tag or not product_id:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # First verify the user
    user = User.query.filter_by(rfid_tag=rfid_tag).first()
    
    if not user:
        logging.warning(f"Unauthorized RFID attempt during item retrieval: {rfid_tag}")
        return jsonify({'error': 'Unauthorized RFID'}), 401
    
    # Check if product exists and has enough stock
    product = Product.query.get(product_id)
    
    if not product:
        logging.warning(f"Product ID not found: {product_id}")
        return jsonify({'error': 'Product not found'}), 404
    
    if product.quantity < quantity:
        logging.warning(f"Insufficient stock for product ID {product_id}: requested {quantity}, available {product.quantity}")
        return jsonify({'error': 'Not enough stock'}), 400
    
    try:
        # Update the product quantity
        product.quantity -= quantity
        
        # Create transaction record
        transaction = Transaction(
            user_id=user.id,
            product_id=product.id,
            quantity=quantity,
            transaction_type='get',
            shelf_id=shelf_id
        )
        db.session.add(transaction)
        
        # Create RFID tracking record
        tracking = RFIDTracking(
            rfid_tag=product.rfid_tag,
            product_id=product.id,
            shelf_id=shelf_id,
            status='removed'
        )
        db.session.add(tracking)
        
        db.session.commit()
        logging.info(f"Item retrieved: Product ID {product.id}, Quantity {quantity}, User ID {user.id}")
        return jsonify({
            'message': 'Item retrieved successfully',
            'product_name': product.name,
            'remaining_quantity': product.quantity
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error retrieving item: {str(e)}")
        return jsonify({'error': f'Error retrieving item: {str(e)}'}), 500