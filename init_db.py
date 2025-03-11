#!/usr/bin/env python
"""
Database initialization script for the Warehouse Management System.
Run this script to initialize the database and create default roles and test data.
"""

from app import create_app
from app.models import db
from app.services.database import initialize_database, _create_default_roles
from app.models.user import User, Role
from app.models.category import Category
from app.models.cabinet import Cabinet, Shelf
from app.models.product import Product
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def init_db():
    """Initialize the database and create test data"""
    app = create_app()
    
    with app.app_context():
        # Initialize database schema
        db.create_all()
        logging.info("Database schema created")
        
        # Create default roles
        _create_default_roles()
        
        # Create test user if not exists
        if not User.query.filter_by(username='admin').first():
            admin_role = Role.query.filter_by(role_name='admin').first()
            admin_user = User(username='admin', password='admin123', rfid_tag='admin-rfid-001')
            admin_user.roles.append(admin_role)
            db.session.add(admin_user)
            logging.info("Created admin user")
            
            # Create test operator if not exists
            operator_role = Role.query.filter_by(role_name='operator').first()
            operator_user = User(username='operator', password='operator123', rfid_tag='operator-rfid-001')
            operator_user.roles.append(operator_role)
            db.session.add(operator_user)
            logging.info("Created operator user")
        
        # Create test categories if not exist
        categories = [
            {"name": "Electronics", "description": "Electronic components and devices"},
            {"name": "Mechanical", "description": "Mechanical parts and tools"},
            {"name": "Consumables", "description": "Items that are consumed during production"}
        ]
        
        for cat_data in categories:
            if not Category.query.filter_by(name=cat_data["name"]).first():
                category = Category(name=cat_data["name"], description=cat_data["description"])
                db.session.add(category)
                logging.info(f"Created category: {cat_data['name']}")
        
        # Commit changes so far to get IDs
        db.session.commit()
        
        # Create test cabinets and shelves if not exist
        if not Cabinet.query.filter_by(name="Cabinet A").first():
            cabinet_a = Cabinet(name="Cabinet A", category_mode="single")
            db.session.add(cabinet_a)
            db.session.commit()
            
            # Add shelves to Cabinet A
            electronics = Category.query.filter_by(name="Electronics").first()
            mechanical = Category.query.filter_by(name="Mechanical").first()
            
            shelf_a1 = Shelf(name="Shelf A1", cabinet_id=cabinet_a.id, allows_multiple_categories=False)
            shelf_a1.categories.append(electronics)
            
            shelf_a2 = Shelf(name="Shelf A2", cabinet_id=cabinet_a.id, allows_multiple_categories=False)
            shelf_a2.categories.append(mechanical)
            
            db.session.add_all([shelf_a1, shelf_a2])
            logging.info("Created Cabinet A with shelves")
            
        # Create test products if not exist
        if not Product.query.filter_by(name="Arduino Nano").first():
            electronics = Category.query.filter_by(name="Electronics").first()
            mechanical = Category.query.filter_by(name="Mechanical").first()
            consumables = Category.query.filter_by(name="Consumables").first()
            
            products = [
                {"name": "Arduino Nano", "barcode": "ARD-001", "rfid_tag": "rfid-ard-001", "quantity": 10, "category_id": electronics.id},
                {"name": "Raspberry Pi 4", "barcode": "RPI-001", "rfid_tag": "rfid-rpi-001", "quantity": 5, "category_id": electronics.id},
                {"name": "Wrench Set", "barcode": "TLS-001", "rfid_tag": "rfid-tls-001", "quantity": 3, "category_id": mechanical.id},
                {"name": "Screwdriver Kit", "barcode": "TLS-002", "rfid_tag": "rfid-tls-002", "quantity": 5, "category_id": mechanical.id},
                {"name": "Solder Wire", "barcode": "CON-001", "rfid_tag": "rfid-con-001", "quantity": 20, "category_id": consumables.id}
            ]
            
            for prod_data in products:
                product = Product(
                    name=prod_data["name"],
                    barcode=prod_data["barcode"],
                    rfid_tag=prod_data["rfid_tag"],
                    quantity=prod_data["quantity"],
                    category_id=prod_data["category_id"]
                )
                db.session.add(product)
                logging.info(f"Created product: {prod_data['name']}")
        
        # Commit all changes
        db.session.commit()
        logging.info("Database initialization completed successfully")

if __name__ == "__main__":
    init_db()
