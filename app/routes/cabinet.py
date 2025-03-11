from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, flash
from app.models import db
from app.models.cabinet import Cabinet, Shelf
from app.models.category import Category
from app.services.opcua_service import write_opcua_value, opcua_log
from sqlalchemy import func
import logging

cabinet_bp = Blueprint('cabinet', __name__, url_prefix='/cabinets')

@cabinet_bp.route('/', methods=['GET'])
def index():
    """List all cabinets"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    cabinets = Cabinet.query.all()
    return render_template('cabinets/index.html', cabinets=cabinets)

@cabinet_bp.route('/add', methods=['GET', 'POST'])
def add():
    """Add a new cabinet"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        name = request.form['name']
        category_mode = request.form.get('category_mode', 'single')
        
        try:
            new_cabinet = Cabinet(name=name, category_mode=category_mode)
            db.session.add(new_cabinet)
            db.session.commit()
            
            logging.info(f"Cabinet added: {name}")
            return redirect(url_for('cabinet.index'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding cabinet: {str(e)}")
            error = "Error adding cabinet. The name may already exist."
            return render_template('cabinets/add.html', error=error)
    
    return render_template('cabinets/add.html')

@cabinet_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    """Edit a cabinet"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    cabinet = Cabinet.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form['name']
        category_mode = request.form.get('category_mode', 'single')
        
        try:
            cabinet.name = name
            cabinet.category_mode = category_mode
            db.session.commit()
            
            logging.info(f"Cabinet updated: ID: {id}, Name: {name}")
            return redirect(url_for('cabinet.index'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating cabinet: {str(e)}")
            error = "Error updating cabinet. The name may already exist."
            return render_template('cabinets/edit.html', cabinet=cabinet, error=error)
    
    return render_template('cabinets/edit.html', cabinet=cabinet)

@cabinet_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    """Delete a cabinet"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    cabinet = Cabinet.query.get_or_404(id)
    
    # Check if the cabinet has shelves
    shelves_count = Shelf.query.filter_by(cabinet_id=id).count()
    
    if shelves_count > 0:
        flash("Cannot delete cabinet because it has shelves", "error")
        return redirect(url_for('cabinet.index'))
    
    try:
        db.session.delete(cabinet)
        db.session.commit()
        logging.info(f"Cabinet deleted: ID: {id}, Name: {cabinet.name}")
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting cabinet: {str(e)}")
        flash(f"Error deleting cabinet: {str(e)}", "error")
    
    return redirect(url_for('cabinet.index'))

@cabinet_bp.route('/shelves/<int:cabinet_id>', methods=['GET'])
def shelves(cabinet_id):
    """List shelves for a specific cabinet"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    cabinet = Cabinet.query.get_or_404(cabinet_id)
    
    # Query shelves with their categories
    shelves_with_categories = db.session.query(
        Shelf,
        func.group_concat(Category.name).label('categories')
    ).outerjoin(
        Shelf.categories
    ).filter(
        Shelf.cabinet_id == cabinet_id
    ).group_by(
        Shelf.id
    ).all()
    
    return render_template('cabinets/shelves.html', cabinet=cabinet, shelves=shelves_with_categories)

@cabinet_bp.route('/shelves/add/<int:cabinet_id>', methods=['GET', 'POST'])
def add_shelf(cabinet_id):
    """Add a shelf to a cabinet"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    cabinet = Cabinet.query.get_or_404(cabinet_id)
    
    if request.method == 'POST':
        name = request.form['name']
        allows_multiple = 'allows_multiple_categories' in request.form
        category_ids = request.form.getlist('categories')
        
        try:
            # Create new shelf
            new_shelf = Shelf(
                cabinet_id=cabinet_id,
                name=name,
                allows_multiple_categories=allows_multiple
            )
            
            # Add categories if any
            if category_ids:
                categories = Category.query.filter(Category.id.in_(category_ids)).all()
                new_shelf.categories = categories
            
            db.session.add(new_shelf)
            db.session.commit()
            
            logging.info(f"Shelf added: Cabinet ID: {cabinet_id}, Name: {name}")
            return redirect(url_for('cabinet.shelves', cabinet_id=cabinet_id))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding shelf: {str(e)}")
            categories = Category.query.all()
            error = f"Error adding shelf: {str(e)}"
            return render_template('cabinets/add_shelf.html', 
                                  cabinet=cabinet, 
                                  categories=categories, 
                                  error=error)
    
    categories = Category.query.all()
    return render_template('cabinets/add_shelf.html', cabinet=cabinet, categories=categories)

@cabinet_bp.route('/shelves/edit/<int:shelf_id>', methods=['GET', 'POST'])
def edit_shelf(shelf_id):
    """Edit a shelf"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    shelf = Shelf.query.get_or_404(shelf_id)
    cabinet = Cabinet.query.get_or_404(shelf.cabinet_id)
    
    if request.method == 'POST':
        name = request.form['name']
        allows_multiple = 'allows_multiple_categories' in request.form
        category_ids = request.form.getlist('categories')
        
        try:
            # Update shelf
            shelf.name = name
            shelf.allows_multiple_categories = allows_multiple
            
            # Update categories
            if category_ids:
                categories = Category.query.filter(Category.id.in_(category_ids)).all()
                shelf.categories = categories
            else:
                shelf.categories = []
            
            db.session.commit()
            
            logging.info(f"Shelf updated: ID: {shelf_id}, Name: {name}")
            return redirect(url_for('cabinet.shelves', cabinet_id=cabinet.id))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating shelf: {str(e)}")
            categories = Category.query.all()
            error = f"Error updating shelf: {str(e)}"
            return render_template('cabinets/edit_shelf.html', 
                                  shelf=shelf,
                                  cabinet=cabinet, 
                                  categories=categories, 
                                  error=error)
    
    categories = Category.query.all()
    return render_template('cabinets/edit_shelf.html', 
                           shelf=shelf,
                           cabinet=cabinet, 
                           categories=categories)

@cabinet_bp.route('/shelves/delete/<int:shelf_id>', methods=['POST'])
def delete_shelf(shelf_id):
    """Delete a shelf"""
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    shelf = Shelf.query.get_or_404(shelf_id)
    cabinet_id = shelf.cabinet_id
    
    try:
        db.session.delete(shelf)
        db.session.commit()
        logging.info(f"Shelf deleted: ID: {shelf_id}, Name: {shelf.name}")
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting shelf: {str(e)}")
        flash(f"Error deleting shelf: {str(e)}", "error")
    
    return redirect(url_for('cabinet.shelves', cabinet_id=cabinet_id))

@cabinet_bp.route('/traffic-light', methods=['POST'])
def traffic_light_control():
    """Control traffic light"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.json
    cabinet_id = data.get('cabinet_id')
    status = data.get('status')  # green, yellow, red
    
    if not cabinet_id or not status:
        return jsonify({'error': 'Missing cabinet_id or status'}), 400
    
    if status not in ['RED', 'YELLOW', 'GREEN', 'OFF']:
        return jsonify({'error': 'Invalid status'}), 400
    
    # Verify cabinet exists
    cabinet = Cabinet.query.get(cabinet_id)
    if not cabinet:
        return jsonify({'error': 'Cabinet not found'}), 404
    
    node_id = f"ns=2;s=TrafficLight_{cabinet_id}"
    result = write_opcua_value(node_id, status)
    
    if 'error' in result:
        return jsonify(result), 500
    
    opcua_log(node_id, status, 'Success')
    return jsonify({'message': f'Traffic light for cabinet {cabinet_id} set to {status}'})

@cabinet_bp.route('/api/list', methods=['GET'])
def api_list():
    """API endpoint to list all cabinets"""
    cabinets = Cabinet.query.all()
    
    result = []
    for cabinet in cabinets:
        result.append({
            'id': cabinet.id,
            'name': cabinet.name,
            'category_mode': cabinet.category_mode,
            'shelves_count': len(cabinet.shelves)
        })
    
    return jsonify(result)