import logging
from flask import current_app
from app.models import db
from app.models.user import User, Role
from app.models.product import Product
from app.models.category import Category
from app.models.cabinet import Cabinet, Shelf
from app.models.transaction import Transaction, RFIDTracking
from tenacity import retry, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def initialize_database():
    """Initialize the database with SQLAlchemy, idempotently"""
    try:
        # Check if tables exist to avoid redundant creation
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if not inspector.get_table_names():
            db.create_all()
            logging.info("Database tables created with SQLAlchemy")
        else:
            logging.debug("Database tables already exist")
        
        # Add default roles if they don't exist
        _create_default_roles()
        logging.info("Database initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing database: {str(e)}")
        raise

def _create_default_roles():
    """Create default roles if they don't exist"""
    default_roles = ['admin', 'user', 'operator']
    with db.session.begin():
        for role_name in default_roles:
            if not Role.query.filter_by(role_name=role_name).first():
                db.session.add(Role(role_name=role_name))
        logging.info("Default roles ensured")

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