from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
from app.models import db
from app.models.product import Product
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.user import User
from sqlalchemy import func, desc
import logging

product_bp = Blueprint('product', __name__, url_prefix='/products')

@product_bp.route('/', methods=['GET'])
def index():
    """List all products"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Query products with their category names
    products = db.session.query(
        Product, Category.name.label('category_name')
    ).outerjoin(
        Category, Product.category_id == Category.id
    ).all()
    
    return render_template('products/index.html', products=products)

@product_bp.route('/add', methods=['GET', 'POST'])
def add():
    """Add a new product"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        name = request.form['name']
        barcode = request.form['barcode']
        category_id = request.form['category_id'] if request.form['category_id'] else None
        rfid_tag = request.form['rfid_tag']
        quantity = request.form.get('quantity', 0, type=int)
        
        try:
            new_product = Product(
                name=name,
                barcode=barcode,
                category_id=category_id,
                rfid_tag=rfid_tag,
                quantity=quantity
            )
            db.session.add(new_product)
            db.session.commit()
            
            logging.info(f"Product added: {name}, Category ID: {category_id}, RFID: {rfid_tag}")
            return redirect(url_for('product.index'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding product: {str(e)}")
            error = "Error adding product. The barcode or RFID tag may already exist."
            
            categories = Category.query.all()
            return render_template('products/add.html', categories=categories, error=error)
    
    categories = Category.query.all()
    return render_template('products/add.html', categories=categories)

@product_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    """Edit a product"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form['name']
        barcode = request.form['barcode']
        category_id = request.form['category_id'] if request.form['category_id'] else None
        rfid_tag = request.form['rfid_tag']
        quantity = request.form.get('quantity', product.quantity, type=int)
        
        try:
            product.name = name
            product.barcode = barcode
            product.category_id = category_id
            product.rfid_tag = rfid_tag
            product.quantity = quantity
            
            db.session.commit()
            logging.info(f"Product updated: ID: {id}, Name: {name}")
            return redirect(url_for('product.index'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating product: {str(e)}")
            error = "Error updating product. The barcode or RFID tag may already exist."
            
            categories = Category.query.all()
            return render_template('products/edit.html', product=product, categories=categories, error=error)
    
    categories = Category.query.all()
    return render_template('products/edit.html', product=product, categories=categories)

@product_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    """Delete a product"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    product = Product.query.get_or_404(id)
    
    try:
        db.session.delete(product)
        db.session.commit()
        logging.info(f"Product deleted: ID: {id}, Name: {product.name}")
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting product: {str(e)}")
        # Handle the error, perhaps show a message to the user
    
    return redirect(url_for('product.index'))

@product_bp.route('/api/list', methods=['GET'])
def api_list():
    """API endpoint to list all products"""
    products_with_categories = db.session.query(
        Product, Category.name.label('category_name')
    ).outerjoin(
        Category, Product.category_id == Category.id
    ).all()
    
    result = []
    for product, category_name in products_with_categories:
        result.append({
            'id': product.id,
            'name': product.name,
            'barcode': product.barcode,
            'category_id': product.category_id,
            'category_name': category_name,
            'rfid_tag': product.rfid_tag,
            'quantity': product.quantity
        })
    
    return jsonify(result)

@product_bp.route('/dashboard')
def dashboard():
    """Show dashboard with product statistics"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Get total product count
    product_count = Product.query.count()
    
    # Get total quantity
    total_quantity = db.session.query(func.sum(Product.quantity)).scalar() or 0
    
    # Get products by category
    products_by_category = db.session.query(
        Category.name.label('category'),
        func.count(Product.id).label('count')
    ).join(
        Product, Product.category_id == Category.id
    ).group_by(
        Category.id
    ).all()
    
    # Get recent transactions
    recent_transactions = db.session.query(
        Transaction.id,
        Transaction.timestamp,
        User.username,
        Product.name.label('product_name'),
        Transaction.quantity,
        Transaction.transaction_type
    ).join(
        User, Transaction.user_id == User.id
    ).join(
        Product, Transaction.product_id == Product.id
    ).order_by(
        desc(Transaction.timestamp)
    ).limit(10).all()
    
    return render_template('products/dashboard.html',
                          product_count=product_count,
                          total_quantity=total_quantity,
                          products_by_category=products_by_category,
                          recent_transactions=recent_transactions)