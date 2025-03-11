from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, flash
from app.models import db
from app.models.category import Category
from app.models.product import Product
import logging

category_bp = Blueprint('category', __name__, url_prefix='/categories')

@category_bp.route('/', methods=['GET'])
def index():
    """List all categories"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    categories = Category.query.all()
    return render_template('categories/index.html', categories=categories)

@category_bp.route('/add', methods=['GET', 'POST'])
def add():
    """Add a new category"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        
        try:
            new_category = Category(name=name, description=description)
            db.session.add(new_category)
            db.session.commit()
            
            logging.info(f"Category added: {name}")
            return redirect(url_for('category.index'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding category: {str(e)}")
            error = "Error adding category. The name may already exist."
            return render_template('categories/add.html', error=error)
        
    return render_template('categories/add.html')

@category_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    """Edit a category"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    category = Category.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        
        try:
            category.name = name
            category.description = description
            db.session.commit()
            
            logging.info(f"Category updated: ID: {id}, Name: {name}")
            return redirect(url_for('category.index'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating category: {str(e)}")
            error = "Error updating category. The name may already exist."
            return render_template('categories/edit.html', category=category, error=error)
    
    return render_template('categories/edit.html', category=category)

@category_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    """Delete a category"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    category = Category.query.get_or_404(id)
    
    # Check if the category is in use
    products_count = Product.query.filter_by(category_id=id).count()
    
    if products_count > 0:
        flash("Cannot delete category because it is in use by products", "error")
        return redirect(url_for('category.index'))
    
    try:
        db.session.delete(category)
        db.session.commit()
        logging.info(f"Category deleted: ID: {id}, Name: {category.name}")
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting category: {str(e)}")
        flash(f"Error deleting category: {str(e)}", "error")
    
    return redirect(url_for('category.index'))

@category_bp.route('/api/list', methods=['GET'])
def api_list():
    """API endpoint to list all categories"""
    categories = Category.query.all()
    
    result = []
    for category in categories:
        result.append({
            'id': category.id,
            'name': category.name,
            'description': category.description
        })
    
    return jsonify(result)