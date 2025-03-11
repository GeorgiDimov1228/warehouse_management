import logging
from flask import current_app
from app.models import db
from app.models.user import User, Role
from app.models.product import Product
from app.models.category import Category
from app.models.cabinet import Cabinet, Shelf
from app.models.transaction import Transaction, RFIDTracking

def initialize_database():
    """Initialize the database with SQLAlchemy"""
    try:
        # Create all tables defined by the models
        db.create_all()
        logging.info("Database initialized successfully with SQLAlchemy")
        
        # Add default roles if they don't exist
        _create_default_roles()
        
    except Exception as e:
        logging.error(f"Error initializing database: {str(e)}")
        raise

def _create_default_roles():
    """Create default roles if they don't exist"""
    default_roles = ['admin', 'user', 'operator']
    
    for role_name in default_roles:
        if Role.query.filter_by(role_name=role_name).first() is None:
            role = Role(role_name=role_name)
            db.session.add(role)
    
    try:
        db.session.commit()
        logging.info("Default roles created")
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating default roles: {str(e)}")

def reset_database():
    """Reset the database by dropping all tables and recreating them"""
    try:
        db.drop_all()
        db.create_all()
        _create_default_roles()
        logging.info("Database has been reset and reinitialized")
    except Exception as e:
        logging.error(f"Error resetting database: {str(e)}")
        raise