from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app.models.user import User
import logging

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Find user by username and password
        user = User.query.filter_by(username=username, password=password).first()
        
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            logging.info(f"User logged in: {username}")
            return redirect(url_for('product.dashboard'))
        
        logging.warning(f"Failed login attempt for username: {username}")
        return render_template('auth/login.html', error='Invalid credentials'), 401
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """Handle user logout"""
    if 'username' in session:
        logging.info(f"User logged out: {session['username']}")
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/status')
def status():
    """Check if user is logged in"""
    if 'user_id' in session:
        return jsonify({'logged_in': True, 'user_id': session['user_id'], 'username': session.get('username')})
    return jsonify({'logged_in': False})

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        rfid_tag = request.form['rfid_tag']
        
        # Check if username or RFID already exists
        if User.query.filter_by(username=username).first():
            return render_template('auth/register.html', error='Username already exists')
        
        if User.query.filter_by(rfid_tag=rfid_tag).first():
            return render_template('auth/register.html', error='RFID tag already exists')
        
        # Create new user
        from app.models import db
        try:
            new_user = User(username=username, password=password, rfid_tag=rfid_tag)
            db.session.add(new_user)
            db.session.commit()
            logging.info(f"New user registered: {username}")
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error registering user: {str(e)}")
            return render_template('auth/register.html', error='Error registering user')
    
    return render_template('auth/register.html')