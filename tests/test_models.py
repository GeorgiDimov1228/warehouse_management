import pytest
from app.models import db
from app.models.user import User, Role
from app.models.product import Product
from app.models.category import Category
from app.models.cabinet import Cabinet, Shelf
from app.models.transaction import Transaction, RFIDTracking

def test_user_creation(app, admin_role):
    """Test user creation and role assignment."""
    with app.app_context():
        user = User(
            username='testuser',
            password='password123',
            rfid_tag='rfid-tag-001'
        )
        user.roles.append(admin_role)
        db.session.add(user)
        db.session.commit()
        
        # Retrieve the user
        saved_user = User.query.filter_by(username='testuser').first()
        assert saved_user is not None
        assert saved_user.username == 'testuser'
        assert saved_user.rfid_tag == 'rfid-tag-001'
        assert len(saved_user.roles) == 1
        assert saved_user.roles[0].role_name == 'admin'

def test_product_creation(app, test_categories):
    """Test product creation and category association."""
    with app.app_context():
        category = test_categories[0]  # Electronics
        
        product = Product(
            name='Test Product',
            barcode='TEST-001',
            rfid_tag='rfid-test-001',
            quantity=15,
            category_id=category.id
        )
        db.session.add(product)
        db.session.commit()
        
        # Retrieve the product
        saved_product = Product.query.filter_by(barcode='TEST-001').first()
        assert saved_product is not None
        assert saved_product.name == 'Test Product'
        assert saved_product.quantity == 15
        assert saved_product.category_id == category.id
        
        # Check the relationship
        assert saved_product.category.name == 'Electronics'

def test_cabinet_and_shelf(app, test_categories):
    """Test cabinet and shelf creation with category assignments."""
    with app.app_context():
        # Create a cabinet
        cabinet = Cabinet(
            name='Storage Cabinet',
            category_mode='multi'
        )
        db.session.add(cabinet)
        db.session.commit()
        
        # Create shelves
        shelf1 = Shelf(
            name='Top Shelf',
            cabinet_id=cabinet.id,
            allows_multiple_categories=True
        )
        shelf2 = Shelf(
            name='Bottom Shelf',
            cabinet_id=cabinet.id,
            allows_multiple_categories=False
        )
        
        # Assign categories
        shelf1.categories.append(test_categories[0])  # Electronics
        shelf1.categories.append(test_categories[1])  # Mechanical
        shelf2.categories.append(test_categories[2])  # Consumables
        
        db.session.add_all([shelf1, shelf2])
        db.session.commit()
        
        # Retrieve cabinet with shelves
        saved_cabinet = Cabinet.query.filter_by(name='Storage Cabinet').first()
        assert saved_cabinet is not None
        assert len(saved_cabinet.shelves) == 2
        
        # Check shelf properties
        shelves = sorted(saved_cabinet.shelves, key=lambda s: s.name)
        assert shelves[1].name == 'Top Shelf'
        assert shelves[1].allows_multiple_categories is True
        assert len(shelves[1].categories) == 2
        
        assert shelves[0].name == 'Bottom Shelf'
        assert shelves[0].allows_multiple_categories is False
        assert len(shelves[0].categories) == 1
        assert shelves[0].categories[0].name == 'Consumables'

def test_transaction_creation(app, test_admin, test_products, test_shelf):
    """Test transaction creation and relationships."""
    with app.app_context():
        product = test_products[0]
        
        # Create a transaction
        transaction = Transaction(
            user_id=test_admin.id,
            product_id=product.id,
            quantity=3,
            transaction_type='move',
            shelf_id=test_shelf.id
        )
        db.session.add(transaction)
        db.session.commit()
        
        # Retrieve the transaction
        saved_transaction = Transaction.query.filter_by(
            user_id=test_admin.id,
            product_id=product.id
        ).first()
        
        assert saved_transaction is not None
        assert saved_transaction.quantity == 3
        assert saved_transaction.transaction_type == 'move'
        assert saved_transaction.shelf_id == test_shelf.id
        
        # Check relationships
        assert saved_transaction.user.username == test_admin.username
        assert saved_transaction.product.name == product.name
        assert saved_transaction.shelf.name == test_shelf.name

def test_rfid_tracking(app, test_products, test_shelf):
    """Test RFID tracking record creation."""
    with app.app_context():
        product = test_products[0]
        
        # Create RFID tracking
        tracking = RFIDTracking(
            rfid_tag=product.rfid_tag,
            product_id=product.id,
            shelf_id=test_shelf.id,
            status='moved'
        )
        db.session.add(tracking)
        db.session.commit()
        
        # Retrieve the tracking record
        saved_tracking = RFIDTracking.query.filter_by(
            rfid_tag=product.rfid_tag
        ).first()
        
        assert saved_tracking is not None
        assert saved_tracking.status == 'moved'
        assert saved_tracking.product_id == product.id
        assert saved_tracking.shelf_id == test_shelf.id
        
        # Check relationships
        assert saved_tracking.product.name == product.name
        assert saved_tracking.shelf.name == test_shelf.name

def test_static_methods(app, test_admin, test_products, test_shelf):
    """Test static helper methods on models."""
    with app.app_context():
        product = test_products[0]
        
        # Test Transaction.add_transaction
        transaction = Transaction.add_transaction(
            user_id=test_admin.id,
            product_id=product.id,
            quantity=5,
            transaction_type='add',
            shelf_id=test_shelf.id
        )
        
        assert transaction is not None
        assert transaction.quantity == 5
        assert transaction.transaction_type == 'add'
        
        # Test RFIDTracking.track_rfid
        tracking = RFIDTracking.track_rfid(
            rfid_tag=product.rfid_tag,
            product_id=product.id,
            shelf_id=test_shelf.id,
            status='scanned'
        )
        
        assert tracking is not None
        assert tracking.rfid_tag == product.rfid_tag
        assert tracking.status == 'scanned'