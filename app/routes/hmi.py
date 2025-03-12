from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
from app.models import db
from app.models.product import Product
from app.models.category import Category
from app.models.cabinet import Cabinet, Shelf
from app.models.transaction import Transaction, RFIDTracking
from app.services.opcua_service import read_opcua_value, write_opcua_value, opcua_log
from sqlalchemy import func
import logging

hmi_bp = Blueprint('hmi', __name__, url_prefix='/hmi')

@hmi_bp.route('/', methods=['GET'])
def index():
    """Main HMI interface - single point of entry for the warehouse management"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Get all categories for product categorization
    categories = Category.query.all()
    
    # Get all cabinets and shelves for placement options
    cabinets = Cabinet.query.all()
    
    # Get recent transactions
    recent_transactions = db.session.query(
        Transaction
    ).order_by(
        Transaction.timestamp.desc()
    ).limit(10).all()
    
    return render_template('hmi/index.html', 
                          categories=categories,
                          cabinets=cabinets,
                          recent_transactions=recent_transactions)

@hmi_bp.route('/add-product', methods=['POST'])
def add_product():
    """Add a new product and determine optimal storage location"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get product data from form
    name = request.form.get('name')
    barcode = request.form.get('barcode')
    rfid_tag = request.form.get('rfid_tag')
    category_id = request.form.get('category_id')
    quantity = int(request.form.get('quantity', 1))
    
    if not all([name, barcode, rfid_tag, category_id]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # Create new product
        new_product = Product(
            name=name,
            barcode=barcode,
            rfid_tag=rfid_tag,
            category_id=category_id,
            quantity=quantity
        )
        db.session.add(new_product)
        db.session.commit()
        
        # Find optimal placement for this product
        placement = find_optimal_placement(new_product.id, category_id)
        
        if placement:
            # If placement found, update OPC UA to indicate where to place the item
            activate_cabinet_indicators(placement['cabinet_id'], placement['shelf_id'])
            
            return jsonify({
                'success': True,
                'product_id': new_product.id,
                'placement': placement
            })
        else:
            return jsonify({
                'success': True,
                'product_id': new_product.id,
                'placement': None,
                'message': 'No suitable storage location found'
            })
            
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding product via HMI: {str(e)}")
        return jsonify({'error': f'Error adding product: {str(e)}'}), 500

@hmi_bp.route('/scan-product', methods=['POST'])
def scan_product():
    """Process a product scan (barcode or RFID)"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    scan_type = request.form.get('scan_type', 'barcode')
    scan_value = request.form.get('scan_value')
    
    if not scan_value:
        return jsonify({'error': 'No scan value provided'}), 400
    
    try:
        # Find product by barcode or RFID
        if scan_type == 'barcode':
            product = Product.query.filter_by(barcode=scan_value).first()
        else:  # RFID
            product = Product.query.filter_by(rfid_tag=scan_value).first()
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Find current location if any
        current_location = get_product_location(product.id)
        
        return jsonify({
            'success': True,
            'product': {
                'id': product.id,
                'name': product.name,
                'barcode': product.barcode,
                'rfid_tag': product.rfid_tag,
                'quantity': product.quantity,
                'category_id': product.category_id
            },
            'location': current_location
        })
            
    except Exception as e:
        logging.error(f"Error scanning product via HMI: {str(e)}")
        return jsonify({'error': f'Error scanning product: {str(e)}'}), 500

@hmi_bp.route('/move-product', methods=['POST'])
def move_product():
    """Move a product to a new location"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    product_id = request.form.get('product_id')
    shelf_id = request.form.get('shelf_id')
    quantity = int(request.form.get('quantity', 1))
    
    if not all([product_id, shelf_id]):
        return jsonify({'error': 'Missing product_id or shelf_id'}), 400
    
    try:
        product = Product.query.get(product_id)
        shelf = Shelf.query.get(shelf_id)
        
        if not product or not shelf:
            return jsonify({'error': 'Product or shelf not found'}), 404
        
        # Create transaction record
        transaction = Transaction(
            user_id=session['user_id'],
            product_id=product_id,
            quantity=quantity,
            transaction_type='move',
            shelf_id=shelf_id
        )
        db.session.add(transaction)
        
        # Create RFID tracking record
        tracking = RFIDTracking(
            rfid_tag=product.rfid_tag,
            product_id=product_id,
            shelf_id=shelf_id,
            status='moved'
        )
        db.session.add(tracking)
        
        db.session.commit()
        
        # Activate cabinet indicators
        cabinet_id = shelf.cabinet_id
        activate_cabinet_indicators(cabinet_id, shelf_id)
        
        return jsonify({
            'success': True,
            'message': f'Product {product.name} moved to {shelf.name} in cabinet {shelf.cabinet.name}'
        })
            
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error moving product via HMI: {str(e)}")
        return jsonify({'error': f'Error moving product: {str(e)}'}), 500

def find_optimal_placement(product_id, category_id):
    """Find the optimal cabinet and shelf for a product"""
    try:
        # Find shelves that accept this category
        suitable_shelves = db.session.query(Shelf).join(
            Shelf.categories
        ).filter(
            Category.id == category_id
        ).all()
        
        if not suitable_shelves:
            logging.warning(f"No suitable shelves found for category {category_id}")
            return None
        
        # Score each shelf based on available space, organization, etc.
        # This is a simple implementation - you might want to enhance this logic
        scored_shelves = []
        for shelf in suitable_shelves:
            # Calculate score based on:
            # 1. Number of products of the same category already on this shelf
            # 2. Available space on the shelf
            products_of_same_category = db.session.query(func.count(Transaction.id)).filter(
                Transaction.shelf_id == shelf.id,
                Transaction.product_id == Product.id,
                Product.category_id == category_id
            ).scalar() or 0
            
            # Higher score for shelves with same category items (consolidation)
            score = products_of_same_category * 10
            
            scored_shelves.append((shelf, score))
        
        # Sort by score and return best match
        if scored_shelves:
            best_shelf = sorted(scored_shelves, key=lambda x: x[1], reverse=True)[0][0]
            cabinet = Cabinet.query.get(best_shelf.cabinet_id)
            
            return {
                'cabinet_id': cabinet.id,
                'cabinet_name': cabinet.name,
                'shelf_id': best_shelf.id,
                'shelf_name': best_shelf.name
            }
        
        # If no scored shelves, just return the first suitable one
        shelf = suitable_shelves[0]
        cabinet = Cabinet.query.get(shelf.cabinet_id)
        
        return {
            'cabinet_id': cabinet.id,
            'cabinet_name': cabinet.name,
            'shelf_id': shelf.id,
            'shelf_name': shelf.name
        }
        
    except Exception as e:
        logging.error(f"Error finding optimal placement: {str(e)}")
        return None

def get_product_location(product_id):
    """Get the current location of a product based on latest transaction"""
    try:
        # Find the latest transaction for this product with a shelf_id
        latest_transaction = Transaction.query.filter(
            Transaction.product_id == product_id,
            Transaction.shelf_id.isnot(None)
        ).order_by(
            Transaction.timestamp.desc()
        ).first()
        
        if not latest_transaction or not latest_transaction.shelf_id:
            return None
        
        shelf = Shelf.query.get(latest_transaction.shelf_id)
        cabinet = Cabinet.query.get(shelf.cabinet_id)
        
        return {
            'cabinet_id': cabinet.id,
            'cabinet_name': cabinet.name,
            'shelf_id': shelf.id,
            'shelf_name': shelf.name,
            'transaction_type': latest_transaction.transaction_type,
            'timestamp': latest_transaction.timestamp.isoformat()
        }
        
    except Exception as e:
        logging.error(f"Error getting product location: {str(e)}")
        return None

def activate_cabinet_indicators(cabinet_id, shelf_id):
    """Send commands to PLC to activate indicators for a cabinet/shelf"""
    try:
        # Set traffic light for cabinet to green
        write_opcua_value(f"ns=2;s=Cabinet_{cabinet_id}_TrafficLight", "GREEN")
        
        # Set shelf indicator (if your PLC supports this)
        write_opcua_value(f"ns=2;s=Cabinet_{cabinet_id}_Shelf_{shelf_id}_Indicator", "ON")
        
        # Log the action
        opcua_log(f"ns=2;s=Cabinet_{cabinet_id}_TrafficLight", "GREEN", "Success")
        opcua_log(f"ns=2;s=Cabinet_{cabinet_id}_Shelf_{shelf_id}_Indicator", "ON", "Success")
        
        return True
    except Exception as e:
        logging.error(f"Error activating cabinet indicators: {str(e)}")
        return False